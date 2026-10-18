import json
from functools import lru_cache
from pathlib import Path

from flask import request
from jsonschema import ValidationError, validate
from sqlalchemy.exc import IntegrityError

from models import db


class APIError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


@lru_cache(maxsize=5)
def load_schema(entity):
    schema_path = Path(__file__).resolve().parent.parent / "schemas" / f"{entity}.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def payload_for(entity, partial=False):
    if not request.is_json:
        raise APIError(415, "Cần Content-Type: application/json")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise APIError(400, "Body phải là một JSON object hợp lệ")
    if partial and not data:
        raise APIError(400, "PATCH cần ít nhất một trường để cập nhật")

    schema = load_schema(entity)
    if partial:
        schema = {**schema, "required": []}

    try:
        validate(instance=data, schema=schema)
    except ValidationError as error:
        raise APIError(400, f"Dữ liệu không hợp lệ: {error.message}") from error

    return data


def get_or_404(model, object_id):
    item = db.session.get(model, object_id)
    if item is None:
        raise APIError(404, f"Không tìm thấy {model.__name__} có id={object_id}")
    return item


def save_changes():
    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        raise APIError(409, "Dữ liệu trùng hoặc vi phạm ràng buộc database") from error
