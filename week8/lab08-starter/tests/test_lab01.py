"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
import pytest
from jsonschema import validate, ValidationError

def test_get_books_empty(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.get_json() == []

def test_get_book_not_found(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"

def test_create_book_missing_title(client):
    response = client.post("/books", json={
        "author": "Ngo Ba Son"
    })

    assert response.status_code == 400

    data = response.get_json()
    assert "title" in [err["field"] for err in data["errors"]]

def test_delete_book_then_get_404(client):
    response = client.post("/books", json={
        "title": "Book 01",
        "author": "Ngo Ba Son",
        "year": 2026
    })

    assert response.status_code == 201
    book_id = response.get_json()["id"]

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204

    result = client.get(f"/books/{book_id}")
    assert result.status_code == 404

def test_response_extra_field_blocked(client):
    response = client.post("/books", json={
        "title": "Test Book",
        "author": "Nguyen Van A",
        "year": 2024
    })

    assert response.status_code == 201
    data = response.get_json()

    schema = {
        "type": "object",
        "required": ["id", "title", "author"],
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "author": {"type": "string"},
            "year": {},
            "isbn": {}
        },
        "additionalProperties": False
    }

    assert "password_hash" not in data
    validate(data, schema)

    data["password_hash"] = "secret"

    with pytest.raises(ValidationError):
        validate(data, schema)