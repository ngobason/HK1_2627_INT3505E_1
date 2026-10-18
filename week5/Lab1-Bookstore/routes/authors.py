from flask import Blueprint, jsonify
from models import Author, db
from routes.common import get_or_404, payload_for, save_changes

bp = Blueprint("authors", __name__)


@bp.get("/authors")
def list_authors():
    items = db.session.execute(db.select(Author).order_by(Author.id)).scalars().all()
    return jsonify([item.to_dict() for item in items])


@bp.get("/authors/<int:author_id>")
def detail_author(author_id):
    return jsonify(get_or_404(Author, author_id).to_dict())


@bp.post("/authors")
def create_author():
    data = payload_for("author")
    item = Author(name=data["name"], bio=data.get("bio"))
    db.session.add(item)
    save_changes()
    return jsonify(item.to_dict()), 201, {"Location": f"/api/v1/authors/{item.id}"}


@bp.patch("/authors/<int:author_id>")
def update_author(author_id):
    item = get_or_404(Author, author_id)
    data = payload_for("author", partial=True)
    for field in ("name", "bio"):
        if field in data:
            setattr(item, field, data[field])
    save_changes()
    return jsonify(item.to_dict())


@bp.delete("/authors/<int:author_id>")
def delete_author(author_id):
    item = get_or_404(Author, author_id)
    db.session.delete(item)
    save_changes()
    return "", 204
