from flask import Flask, jsonify, request
app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Clean Architecture", "author": "Robert C. Martin"},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt"},
    {"id": 4, "title": "Design Patterns", "author": "Erich Gamma"},
    {"id": 5, "title": "Flask Web Development", "author": "Miguel Grinberg"},
    {"id": 6, "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": 7, "title": "Learning JavaScript", "author": "Ethan Brown"},
    {"id": 8, "title": "Node.js in Action", "author": "Mike Cantelon"},
    {"id": 9, "title": "Cloud Computing", "author": "Thomas Erl"},
    {"id": 10, "title": "Software Architecture in Practice", "author": "Len Bass"}
]
next_book_id = 11

def find_book_by_id(book_id):
  return next((b for b in BOOKS if b["id"] == book_id), None)

@app.route("/books", methods=["GET"])
def list_book():
  limit = int(request.args.get("limit", 3))
  return jsonify({"Books": BOOKS[:limit]}), 200

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
  book = find_book_by_id(book_id)
  if book is None:
    return jsonify({"error": "Not found"}), 404
  return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_book():
  global next_book_id
  data = request.get_json(silent=True) or {}
  t, a = data.get("title"), data.get("author")
  if not t or not a:
    return jsonify({"error": "must have title and author"}), 400
  book = {
    "id": next_book_id,
    "title": t,
    "author": a
  }
  next_book_id += 1
  BOOKS.append(book)
  return jsonify(book), 201, {"Location":f"/books/{book['id']}"}

@app.route("/books/<int:book_id>", methods=["PATCH", "DELETE"])
def modify_book(book_id):
  book = find_book_by_id(book_id)
  if book is None:
    return jsonify({"error": "Not found"}), 404
  if request.method == "PATCH":
    book.update(request.get_json(silent=True) or {})
    return jsonify(book), 200
  BOOKS.remove(book)
  return "", 204

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)