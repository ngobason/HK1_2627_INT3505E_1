from flask import Blueprint, jsonify, request

from sqlalchemy import func

from models import Author, Book, Category, db
from routes.common import APIError, get_or_404, payload_for, save_changes
from routes.book_pagination import (
    MAX_LIMIT, DEFAULT_LIMIT, apply_cursor, make_cursor, order_columns,
    parse_genre, parse_positive_int, parse_sort,
)

bp = Blueprint("books", __name__)


def resolve_relations(data):
    """Kiểm tra FK và tìm danh sách Author; chỉ xử lý khi field xuất hiện."""
    category = None
    authors = None

    if "category_id" in data:
        category = get_or_404(Category, data["category_id"])

    if "author_ids" in data:
        ids = data["author_ids"]
        authors = list(db.session.query(Author).filter(Author.id.in_(ids)).all()) if ids else []
        if len(authors) != len(ids):
            raise APIError(400, "author_ids chứa tác giả không tồn tại")

    return category, authors


@bp.get("/books")
def list_books():
    """GET /books?strategy=offset|cursor&limit=2&offset=0&genre=fiction&sort=price,-title."""
    strategy = request.args.get("strategy", "offset")
    if strategy not in {"offset", "cursor"}:
        raise APIError(400, "bad_strategy")
    limit = parse_positive_int(request.args.get("limit", str(DEFAULT_LIMIT)), "bad_limit", max_value=MAX_LIMIT)
    genre = parse_genre(request.args.get("genre"))
    sort, fields = parse_sort(request.args.get("sort", "-id"))
    # Join Category: thể loại là Category.slug, cũng hỗ trợ sort=genre.
    stmt = db.select(Book).join(Category, Book.category_id == Category.id)
    if genre is not None:
        stmt = stmt.where(Category.slug == genre)

    if strategy == "offset":
        if "cursor" in request.args:
            raise APIError(400, "cursor_requires_cursor_strategy")
        offset = parse_positive_int(request.args.get("offset", "0"), "bad_offset", min_value=0)
        total_stmt = db.select(func.count(Book.id)).join(Category, Book.category_id == Category.id)
        if genre is not None:
            total_stmt = total_stmt.where(Category.slug == genre)
        total = db.session.scalar(total_stmt)
        rows = db.session.scalars(stmt.order_by(*order_columns(fields)).offset(offset).limit(limit + 1)).all()
        page = rows[:limit]
        more = len(rows) > limit
        return jsonify({
            "data": [book.to_dict() for book in page],
            "strategy": "offset", "more": more,
            "page": {"offset": offset, "next": offset + limit if more else None, "total": total},
        })

    if "offset" in request.args:
        raise APIError(400, "offset_requires_offset_strategy")
    stmt = apply_cursor(stmt, request.args.get("cursor"), sort, genre, fields)
    rows = db.session.scalars(stmt.order_by(*order_columns(fields)).limit(limit + 1)).all()
    page = rows[:limit]
    more = len(rows) > limit
    next_cursor = make_cursor(page[-1], sort, genre, fields) if more and page else None
    return jsonify({
        "data": [book.to_dict() for book in page],
        "strategy": "cursor", "more": more,
        "page": {"next": next_cursor},
    })


@bp.get("/books/<int:book_id>")
def detail_book(book_id):
    return jsonify(get_or_404(Book, book_id).to_dict())


@bp.post("/books")
def create_book():
    data = payload_for("book")
    category, authors = resolve_relations(data)

    book = Book(
        title=data["title"],
        isbn=data["isbn"],
        price_vnd=data["price_vnd"],
        stock=data["stock"],
        category=category,
        authors=authors if authors is not None else [],
    )
    db.session.add(book)
    save_changes()
    return jsonify(book.to_dict()), 201, {"Location": f"/api/v1/books/{book.id}"}


@bp.patch("/books/<int:book_id>")
def update_book(book_id):
    book = get_or_404(Book, book_id)
    data = payload_for("book", partial=True)
    category, authors = resolve_relations(data)

    for field in ("title", "isbn", "price_vnd", "stock"):
        if field in data:
            setattr(book, field, data[field])
    if category is not None:
        book.category = category
    if authors is not None:
        book.authors = authors

    save_changes()
    return jsonify(book.to_dict())


@bp.delete("/books/<int:book_id>")
def delete_book(book_id):
    book = get_or_404(Book, book_id)
    if book.reviews:
        raise APIError(409, "Không thể xóa sách đang có Review; hãy xóa Review trước")
    db.session.delete(book)
    save_changes()
    return "", 204
