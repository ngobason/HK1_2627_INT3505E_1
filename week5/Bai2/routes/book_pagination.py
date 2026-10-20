import base64
import json
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import and_, or_

from models import Book, Category
from routes.common import APIError

CURSOR_VERSION = 1
MAX_CURSOR_LENGTH = 4096
DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# Whitelist: không sử dụng tên cột SQL trực tiếp từ query string.
SORT_COLUMNS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title,
    "stock": Book.stock,
    "genre": Category.slug,
}


@dataclass(frozen=True)
class SortField:
    name: str
    column: Any
    descending: bool


def parse_sort(raw: str):
    """Trả về (canonical_sort, các cột để order/filter), luôn có tie-break id."""
    if not isinstance(raw, str) or not raw or len(raw) > 160:
        raise APIError(400, "bad_sort")
    fields = []
    used = set()
    for token in raw.split(","):
        token = token.strip()
        descending = token.startswith("-")
        name = token[1:] if descending else token
        if name not in SORT_COLUMNS or name in used:
            raise APIError(400, "bad_sort")
        used.add(name)
        fields.append(SortField(name, SORT_COLUMNS[name], descending))
    if "id" not in used:
        fields.append(SortField("id", Book.id, False))
    normalized = ",".join(("-" if field.descending else "") + field.name for field in fields if field.name in used)
    return normalized, fields


def parse_positive_int(raw: str, code: str, *, min_value=1, max_value=None):
    if not isinstance(raw, str) or not re.fullmatch(r"[0-9]{1,12}", raw):
        raise APIError(400, code)
    number = int(raw)
    if number < min_value or (max_value is not None and number > max_value):
        raise APIError(400, code)
    return number


def parse_genre(raw):
    """Genre dùng slug của Category, ví dụ fiction, science-fiction."""
    if raw is None:
        return None
    if not isinstance(raw, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", raw) or len(raw) > 100:
        raise APIError(400, "bad_genre")
    return raw


def order_columns(fields):
    return [field.column.desc() if field.descending else field.column.asc() for field in fields]


def extract_value(book, field):
    if field.name == "genre":
        return book.category.slug
    if field.name == "price":
        return book.price_vnd
    return getattr(book, field.name)


def _encode(payload):
    value = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")


def _decode(raw):
    if not isinstance(raw, str) or len(raw) > MAX_CURSOR_LENGTH or not re.fullmatch(r"[A-Za-z0-9_-]+", raw):
        raise APIError(400, "bad_cursor")
    try:
        decoded = base64.b64decode(raw + "=" * (-len(raw) % 4), altchars=b"-_", validate=True)
        item = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeError, TypeError, OverflowError) as error:
        raise APIError(400, "bad_cursor") from error
    if not isinstance(item, dict) or set(item) != {"v", "s", "g", "values"}:
        raise APIError(400, "bad_cursor")
    if type(item["v"]) is not int or item["v"] != CURSOR_VERSION:
        raise APIError(400, "bad_cursor")
    if not isinstance(item["s"], str) or not isinstance(item["values"], list):
        raise APIError(400, "bad_cursor")
    if item["g"] is not None and not isinstance(item["g"], str):
        raise APIError(400, "bad_cursor")
    return item


def make_cursor(book, sort, genre, fields):
    return _encode({
        "v": CURSOR_VERSION,
        "s": sort,
        "g": genre,
        "values": [extract_value(book, field) for field in fields],
    })


def apply_cursor(stmt, raw, sort, genre, fields):
    """Điều kiện lexicographic: OR(col1 > x1, col1=x1 AND col2 < x2, ...)."""
    if raw is None:
        return stmt
    cursor = _decode(raw)
    if cursor["s"] != sort:
        raise APIError(400, "sort_changed")
    if cursor["g"] != genre:
        raise APIError(400, "filter_changed")
    values = cursor["values"]
    if len(values) != len(fields):
        raise APIError(400, "bad_cursor")

    for value, field in zip(values, fields):
        if field.name in {"id", "price", "stock"}:
            if type(value) is not int or value < (1 if field.name == "id" else 0):
                raise APIError(400, "bad_cursor")
        else:
            if not isinstance(value, str) or len(value) > 200:
                raise APIError(400, "bad_cursor")

    conditions = []
    for i, (value, field) in enumerate(zip(values, fields)):
        prev_equals = [fields[j].column == values[j] for j in range(i)]
        inequality = field.column < value if field.descending else field.column > value
        conditions.append(and_(*prev_equals, inequality))
    return stmt.where(or_(*conditions))
