from flask import Blueprint
from .users_data import get_user
from datetime import datetime, timezone
from email.utils import format_datetime

bp = Blueprint("v1", __name__, url_prefix="/users")

V1_SUNSET = datetime(
    2026, 12, 31, 23, 59, 59,
    tzinfo=timezone.utc
)

@bp.after_request
def add_sunset_header(response):
    response.headers["Sunset"] = format_datetime(
        V1_SUNSET,
        usegmt=True
    )
    return response

@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)

    if not u:
        return {"error": "nf"}, 404

    return {
        "id": uid,
        "full_name": f"{u['first_name']} {u['last_name']}",
        "email": u["email"]
    }
