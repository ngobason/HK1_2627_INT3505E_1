import base64
import json
import re

from sqlalchemy import tuple_

from models import Book
from routes.common import APIError

SORT = {"id": Book.id, "price": Book.price_vnd}
CURSOR_VERSION = 1


def parse_sort(raw):
    if not isinstance(raw, str):
        raise APIError(400, "bad_sort")
    raw = raw.strip()
    desc = raw.startswith("-")
    key = raw[1:] if desc else raw
    if key not in SORT:
        raise APIError(400, "bad_sort")

    p = SORT[key]
    columns = [p.desc() if desc else p.asc()]
    if key != "id":
        columns.append(Book.id.desc() if desc else Book.id.asc())
    return p, columns, desc


def _enc(payload):
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return base64.urlsafe_b64encode(data.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_cursor(raw):
    if not isinstance(raw, str) or len(raw) > 2048 or not re.fullmatch(r"[A-Za-z0-9_-]+", raw):
        raise APIError(400, "bad_cursor")
    try:
        padded = raw + "=" * (-len(raw) % 4)
        decoded = base64.b64decode(padded, altchars=b"-_", validate=True)
        cursor = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise APIError(400, "bad_cursor") from error

    if not isinstance(cursor, dict) or set(cursor) != {"v", "s", "f", "c", "i"}:
        raise APIError(400, "bad_cursor")
    if type(cursor["v"]) is not int or cursor["v"] != CURSOR_VERSION:
        raise APIError(400, "bad_cursor")
    if type(cursor["i"]) is not int or cursor["i"] < 1:
        raise APIError(400, "bad_cursor")
    if type(cursor["c"]) is not int or cursor["c"] < 0:
        raise APIError(400, "bad_cursor")
    if cursor["f"] is not None and (type(cursor["f"]) is not int or cursor["f"] < 1):
        raise APIError(400, "bad_cursor")
    if cursor["s"] not in {"id", "-id", "price", "-price"}:
        raise APIError(400, "bad_cursor")
    if cursor["s"].lstrip("-") == "id" and cursor["c"] != cursor["i"]:
        raise APIError(400, "bad_cursor")
    return cursor


def apply_cursor(query, raw, sort, p, desc, category_id=None):
    """Keyset filter theo sort value + id; không dùng OFFSET."""
    if raw is None:
        return query

    cursor = _decode_cursor(raw)
    if cursor["s"] != sort:
        raise APIError(400, "sort_chg")
    if cursor["f"] != category_id:
        raise APIError(400, "filter_chg")

    op = "<" if desc else ">"
    if sort.lstrip("-") == "id":
        return query.filter(Book.id < cursor["i"] if desc else Book.id > cursor["i"])

    pair = tuple_(p, Book.id)
    value = (cursor["c"], cursor["i"])
    return query.filter(pair.op(op)(value))


def build_response(items, limit, sort, p, more, category_id=None):
    """Trả data + next cursor (nếu còn trang) + more."""
    page = items[:limit]
    next_cursor = None
    if more and page:
        last = page[-1]
        next_cursor = _enc({
            "v": CURSOR_VERSION,
            "s": sort,
            "f": category_id,
            "c": getattr(last, p.key),
            "i": last.id,
        })
    return {
        "data": [book.to_dict() for book in page],
        "page": {"next": next_cursor},
        "more": more,
    }
