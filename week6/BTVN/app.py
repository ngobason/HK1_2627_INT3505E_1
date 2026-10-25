import os
import re
import time
from collections import defaultdict
from datetime import timedelta
from threading import Lock
from uuid import UUID

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    get_jwt, get_jwt_identity, jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

SECRET = os.getenv("JWT_SECRET_KEY", "")
PASSWORD = os.getenv("DEMO_PASSWORD", "")
if len(SECRET.encode()) < 32 or not PASSWORD:
    raise RuntimeError("Cần đặt JWT_SECRET_KEY (>=32 byte) và DEMO_PASSWORD.")

app = Flask(__name__)
app.json.ensure_ascii = False
app.config.update(
    JWT_SECRET_KEY=SECRET,
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
    JWT_ALGORITHM="HS256",
)
jwt = JWTManager(app)

pwd_hash = generate_password_hash(PASSWORD)
USERS = {
    "an@example.com": {"id": "1", "hash": pwd_hash, "role": "user", "scopes": ["posts:read"], "active": True},
    "binh@example.com": {"id": "2", "hash": pwd_hash, "role": "user", "scopes": [], "active": True},
    "admin@example.com": {"id": "3", "hash": pwd_hash, "role": "admin", "scopes": ["posts:read"], "active": True},
}
POSTS = {
    "550e8400-e29b-41d4-a716-446655440000": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "author_id": "1", "content": "Bài công khai của An", "visibility": "public",
        "created_at": "2026-10-25T09:30:00Z",
    },
    "550e8400-e29b-41d4-a716-446655440001": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "author_id": "2", "content": "Bài riêng tư của Bình", "visibility": "private",
        "created_at": "2026-10-25T09:45:00Z",
    },
}
used_refresh = set()               
requests_by_ip = defaultdict(list)
lock = Lock()


def error(status, code, message):
    return jsonify(error=code, message=message), status


def token_pair(user):
    claims = {"scopes": user["scopes"]}
    response = jsonify(
        access_token=create_access_token(user["id"], additional_claims=claims),
        refresh_token=create_refresh_token(user["id"]),
        token_type="Bearer", expires_in=900,
    )
    response.headers["Cache-Control"] = "no-store"
    return response


def token_error(_reason=None):
    refresh = request.path == "/auth/refresh"
    code = "invalid_refresh_token" if refresh else "unauthorized"
    return error(401, code, "Token không hợp lệ hoặc đã hết hạn")


jwt.unauthorized_loader(token_error)
jwt.invalid_token_loader(token_error)
jwt.expired_token_loader(lambda _h, _p: token_error())
jwt.revoked_token_loader(lambda _h, _p: token_error())


@jwt.token_in_blocklist_loader
def is_revoked(_header, claims):
    with lock:
        return claims["type"] == "refresh" and claims["jti"] in used_refresh


@app.before_request
def rate_limit():
    key = (request.remote_addr, request.path)
    now = time.time()
    limit = 5 if request.path == "/auth/login" else 60
    with lock:
        recent = [t for t in requests_by_ip[key] if now - t < 60]
        if len(recent) >= limit:
            return jsonify(error="rate_limited", message="Quá nhiều yêu cầu"), 429, {"Retry-After": "60"}
        requests_by_ip[key] = recent + [now]


@app.post("/auth/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or set(data) != {"email", "password"}:
        return error(400, "validation_error", "Cần email và password")
    email, password = data["email"], data["password"]
    if (not isinstance(email, str) or len(email) > 254 or
        not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or
        not isinstance(password, str) or not password):
        return error(400, "validation_error", "Email hoặc password không hợp lệ")
    user = USERS.get(email)
    if not user or not check_password_hash(user["hash"], password) or not user["active"]:
        return error(401, "invalid_credentials", "Thông tin đăng nhập không đúng")
    return token_pair(user)


@app.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    claims = get_jwt()
    user = next((u for u in USERS.values() if u["id"] == get_jwt_identity()), None)
    if not user:
        return token_error()
    if not user["active"]:
        return error(403, "account_disabled", "Tài khoản bị vô hiệu hóa")
    with lock:
        if claims["jti"] in used_refresh:
            return token_error()
        used_refresh.add(claims["jti"])
    return token_pair(user)


@app.get("/posts/<post_id>")
@jwt_required()
def get_post(post_id):
    try:
        post_id = str(UUID(post_id))
    except ValueError:
        return error(400, "invalid_post_id", "ID không hợp lệ")

    user = next((u for u in USERS.values() if u["id"] == get_jwt_identity()), None)
    if not user or not user["active"]:
        return token_error()
    if "posts:read" not in get_jwt().get("scopes", []):
        return error(403, "insufficient_scope", "Thiếu quyền posts:read")

    post = POSTS.get(post_id)
    if not post or (post["visibility"] == "private" and
                    user["id"] != post["author_id"] and user["role"] != "admin"):
        return error(404, "post_not_found", "Không tìm thấy bài viết")
    return jsonify(post)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
