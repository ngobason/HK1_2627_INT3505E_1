from flask import Blueprint, jsonify
from models import Category, db
from routes.common import APIError, get_or_404, payload_for, save_changes

bp = Blueprint("categories", __name__)


@bp.get("/categories")
def list_categories():
    items = db.session.execute(db.select(Category).order_by(Category.id)).scalars().all()
    return jsonify([item.to_dict() for item in items])


@bp.get("/categories/<int:category_id>")
def detail_category(category_id):
    return jsonify(get_or_404(Category, category_id).to_dict())


@bp.post("/categories")
def create_category():
    data = payload_for("category")
    item = Category(name=data["name"], slug=data["slug"])
    db.session.add(item)
    save_changes()
    return jsonify(item.to_dict()), 201, {"Location": f"/api/v1/categories/{item.id}"}


@bp.patch("/categories/<int:category_id>")
def update_category(category_id):
    item = get_or_404(Category, category_id)
    data = payload_for("category", partial=True)
    for field in ("name", "slug"):
        if field in data:
            setattr(item, field, data[field])
    save_changes()
    return jsonify(item.to_dict())


@bp.delete("/categories/<int:category_id>")
def delete_category(category_id):
    item = get_or_404(Category, category_id)
    if item.books:
        raise APIError(409, "Không thể xóa Category còn sách")
    db.session.delete(item)
    save_changes()
    return "", 204
