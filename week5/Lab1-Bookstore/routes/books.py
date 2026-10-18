from flask import Blueprint, jsonify
from models import Author, Book, Category, db
from routes.common import APIError, get_or_404, payload_for, save_changes

bp = Blueprint("books", __name__)


def resolve_relations(data):
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
    books = db.session.execute(db.select(Book).order_by(Book.id)).scalars().all()
    return jsonify([book.to_dict() for book in books])


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
        raise APIError(409, "Không thể xóa sách đang có Review")
    db.session.delete(book)
    save_changes()
    return "", 204
