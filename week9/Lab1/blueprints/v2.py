from flask import Blueprint, request
from .users_data import get_user, create_user

bp = Blueprint("v2", __name__, url_prefix="/users")


@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)

    if not u:
        return {"error": "nf"}, 404

    return {
        "id": uid,
        "first_name": u["first_name"],
        "last_name": u["last_name"],
        "email": u["email"]
    }

@bp.route("/", methods=["POST"], strict_slashes=False)
def create():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Invalid JSON body"}, 400

    required = ["first_name", "last_name", "email"]

    for field in required:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return {"error": f"{field} is required"}, 400

    user = create_user(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"]
    )

    return user, 201