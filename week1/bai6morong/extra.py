from flask import Flask, jsonify, request
app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    {"id": 2, "title": "Clean Architecture", "author": "Robert C. Martin", "year": 2017},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "year": 1999},
    {"id": 4, "title": "Design Patterns", "author": "Erich Gamma", "year": 1994},
    {"id": 5, "title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018},
    {"id": 6, "title": "Python Crash Course", "author": "Eric Matthes", "year": 2019},
    {"id": 7, "title": "Learning JavaScript", "author": "Ethan Brown", "year": 2016},
    {"id": 8, "title": "Node.js in Action", "author": "Mike Cantelon", "year": 2013},
    {"id": 9, "title": "Cloud Computing", "author": "Thomas Erl", "year": 2013},
    {"id": 10, "title": "Software Architecture in Practice", "author": "Len Bass", "year": 2021},
]
next_book_id = 11

def find_book_by_id(book_id):
  return next((b for b in BOOKS if b["id"] == book_id), None)



@app.route("/books", methods=["GET"])
def list_book():
  limit = int(request.args.get("limit", 3))

  #tim kiem theo GET /books?q=...
  q = request.args.get("q", "").strip().lower()

  #sort theo title
  sort_by = request.args.get("sort")
  order = request.args.get("order", "asc")

  books = BOOKS

  #xu ly q
  if q:
    books = [b for b in books if q in b["title"].lower()]

  #xu ly sort
  if sort_by == "title":
    books = sorted(books, key=lambda book: book["title"], reverse=(order=="desc"))
  
  return jsonify({"Books": books[:limit]}), 200



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
  y = data.get("year")
  if not t or not a:
    return jsonify({"error": "must have title and author"}), 400
  
  # year >= 1900
  if not isinstance(y, int):
    return jsonify({"error": "year must be an integer"}), 400
  if y < 1900:
    return jsonify({"error": "year must >= 1900"}), 400
  
  book = {
    "id": next_book_id,
    "title": t,
    "author": a,
    "year": y
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
    data = request.get_json(silent=True) or {}
    if "year" in data:
      y = data.get("year")
      # year >= 1900
      if not isinstance(y, int):
        return jsonify({"error": "year must be an integer"}), 400
      if y < 1900:
        return jsonify({"error": "year must >= 1900"}), 400
    book.update(data)
    return jsonify(book), 200
  
  BOOKS.remove(book)
  return "", 204

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)