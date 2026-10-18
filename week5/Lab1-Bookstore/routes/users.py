from flask import Blueprint, jsonify
from models import User, db
from routes.common import APIError, get_or_404, payload_for, save_changes

bp = Blueprint("users", __name__)


@bp.get("/users")
def list_users():
    items = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
    return jsonify([item.to_dict() for item in items])


@bp.get("/users/<int:user_id>")
def detail_user(user_id):
    return jsonify(get_or_404(User, user_id).to_dict())


@bp.post("/users")
def create_user():
    data = payload_for("user")
    item = User(email=data["email"], display_name=data["display_name"])
    db.session.add(item)
    save_changes()
    return jsonify(item.to_dict()), 201, {"Location": f"/api/v1/users/{item.id}"}


@bp.patch("/users/<int:user_id>")
def update_user(user_id):
    item = get_or_404(User, user_id)
    data = payload_for("user", partial=True)
    for field in ("email", "display_name"):
        if field in data:
            setattr(item, field, data[field])
    save_changes()
    return jsonify(item.to_dict())


@bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    item = get_or_404(User, user_id)
    if item.reviews:
        raise APIError(409, "Không thể xóa User đang có Review")
    db.session.delete(item)
    save_changes()
    return "", 204
