from flask import Flask, jsonify, request, make_response
app = Flask(__name__)
BOOKS = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "price": 25.99
    },
    {
        "id": 2,
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "isbn": "9780134494166",
        "price": 30.50
    },
    {
        "id": 3,
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "isbn": "9780135957059",
        "price": 27.99
    },
    {
        "id": 4,
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "isbn": "9780201633610",
        "price": 35.00
    },
    {
        "id": 5,
        "title": "Flask Web Development",
        "author": "Miguel Grinberg",
        "isbn": "9781491991732",
        "price": 29.99
    }
]

#Tra ve sach theo id
@app.get("/books/<int:book_id>")
def get_book(book_id):
  idx = next((k for k, b in enumerate(BOOKS) if b["id"] == book_id), None)
  if idx is None:
    return jsonify({"Error": "Book not found"}), 404
  resp = make_response(jsonify(BOOKS[idx]), 200)
  resp.headers["Cache-Control"] = "max-age=60"
  return resp

#Thay toan bo title + author
@app.put("/books/<int:book_id>")
def modify_book(book_id):
  idx = next((k for k, b in enumerate(BOOKS) if b["id"] == book_id), None)
  if idx is None:
    return jsonify({"error": "Book not found"}, 404)
  new_data = request.get_json(silent=True) or {}
  t, a = (new_data.get("title") or "").strip(), (new_data.get("author") or "").strip()
  if not t or not a:
    return jsonify({"error": "Must have title and author"}), 422
  BOOKS[idx] = {
    "id": book_id,
    "title": t,
    "author": a,
    "isbn": new_data.get("isbn"),
    "price": new_data.get("price")
  }
  return jsonify(BOOKS[idx]), 200

#Cap nhat 1 phan thong tin sach
@app.patch("/books/<int:book_id>")
def patch(book_id):
  idx = next((k for k, b in enumerate(BOOKS) if b["id"] == book_id), None)
  if idx is None:
      return jsonify({"error": "Book not found"}), 404
  data = request.get_json(silent=True) or {}
  if data.get("price", 0) < 0:
    return jsonify({"error": "Price must be positive"}), 422
  for i in "title author isbn price".split():
    if i in data:
      BOOKS[idx][i] = data[i]
  return jsonify(BOOKS[idx]), 200

#Xoa sach
@app.delete("/books/<int:book_id>")
def delete_book(book_id):
  idx = next((k for k, b in enumerate(BOOKS) if b["id"] == book_id), None)
  if idx is None:
    return jsonify({"error": "Book not found"}), 404
  BOOKS.pop(idx)
  return "", 204


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)