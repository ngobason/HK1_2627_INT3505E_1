from flask import Flask, jsonify, request
from functools import wraps
import jwt

app = Flask(__name__)

JWT_SECRET = "petstore-secret"
ALLOWED_STATUS = {"available", "pending", "sold"}

PETS = [
    {"id": 1, "name": "Milo", "tag": "cat", "status": "available"},
    {"id": 2, "name": "Lucky", "tag": "dog", "status": "pending"},
]


def problem(status, title, detail, error_type, instance=None):
    body = {
        "type": f"https://api.petstore.com/errors/{error_type}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance or request.path,
    }
    response = jsonify(body)
    response.status_code = status
    response.content_type = "application/problem+json"
    return response


def require_jwt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return problem(
                401,
                "Unauthorized",
                "Bearer token is missing or invalid",
                "unauthorized",
            )

        token = auth[7:].strip()

        try:
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return problem(
                401,
                "Unauthorized",
                "Bearer token is missing or invalid",
                "unauthorized",
            )

        return func(*args, **kwargs)

    return wrapper


def find_pet(pet_id):
    return next((pet for pet in PETS if pet["id"] == pet_id), None)


def validate_pet_fields(data, partial=False):
    allowed = {"name", "tag", "status"}

    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    unknown = set(data) - allowed
    if unknown:
        return f"Unknown field(s): {', '.join(sorted(unknown))}"

    if not partial:
        for field in ("name", "status"):
            if field not in data:
                return f"{field} is required"

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return "name must not be empty"
        if len(data["name"]) > 100:
            return "name must be at most 100 characters"

    if "tag" in data and data["tag"] is not None:
        if not isinstance(data["tag"], str):
            return "tag must be a string"
        if len(data["tag"]) > 50:
            return "tag must be at most 50 characters"

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        return "status must be one of: available, pending, sold"

    return None


@app.get("/v1/pets")
def list_pets():
    raw_limit = request.args.get("limit", "20")

    try:
        limit = int(raw_limit)
    except ValueError:
        return problem(
            400,
            "Bad request",
            "limit must be an integer",
            "bad-request",
        )

    if limit < 1 or limit > 100:
        return problem(
            400,
            "Bad request",
            "limit must be between 1 and 100",
            "bad-request",
        )

    return jsonify(PETS[:limit]), 200


@app.post("/v1/pets")
@require_jwt
def create_pet():
    data = request.get_json(silent=True)

    if data is None:
        return problem(
            400,
            "Bad request",
            "Request body must contain valid JSON",
            "bad-request",
        )

    error = validate_pet_fields(data)
    if error:
        return problem(
            422,
            "Validation failed",
            error,
            "validation-error",
        )

    new_pet = {
        "id": max((pet["id"] for pet in PETS), default=0) + 1,
        "name": data["name"].strip(),
        "tag": data.get("tag"),
        "status": data["status"],
    }

    PETS.append(new_pet)

    response = jsonify(new_pet)
    response.status_code = 201
    response.headers["Location"] = f"/v1/pets/{new_pet['id']}"
    return response


@app.get("/v1/pets/<int:pet_id>")
def get_pet_by_id(pet_id):
    pet = find_pet(pet_id)

    if pet is None:
        return problem(
            404,
            "Pet not found",
            f"Pet with id {pet_id} was not found",
            "pet-not-found",
        )

    return jsonify(pet), 200


@app.patch("/v1/pets/<int:pet_id>")
@require_jwt
def patch_pet(pet_id):
    pet = find_pet(pet_id)

    if pet is None:
        return problem(
            404,
            "Pet not found",
            f"Pet with id {pet_id} was not found",
            "pet-not-found",
        )

    data = request.get_json(silent=True)

    if data is None:
        return problem(
            400,
            "Bad request",
            "Request body must contain valid JSON",
            "bad-request",
        )

    if not data:
        return problem(
            400,
            "Bad request",
            "At least one field must be provided",
            "bad-request",
        )

    error = validate_pet_fields(data, partial=True)
    if error:
        return problem(
            422,
            "Validation failed",
            error,
            "validation-error",
        )

    if "name" in data:
        pet["name"] = data["name"].strip()

    if "tag" in data:
        pet["tag"] = data["tag"]

    if "status" in data:
        pet["status"] = data["status"]

    return jsonify(pet), 200


@app.delete("/v1/pets/<int:pet_id>")
@require_jwt
def delete_pet(pet_id):
    pet = find_pet(pet_id)

    if pet is None:
        return problem(
            404,
            "Pet not found",
            f"Pet with id {pet_id} was not found",
            "pet-not-found",
        )

    PETS.remove(pet)
    return "", 204


@app.errorhandler(500)
def internal_server_error(_error):
    return problem(
        500,
        "Internal server error",
        "An unexpected error occurred",
        "internal-server-error",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
