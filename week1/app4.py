from flask import Flask, jsonify, request
app = Flask(__name__)

BOOKS = [
    {"id": "1", "title": "Python Basics"},
    {"id": "2", "title": "Flask Web Development Python"},
    {"id": "3", "title": "REST API Design"},
    {"id": "4", "title": "Learning Python and Java"},
    {"id": "5", "title": "Node.js in Action"},
    {"id": "6", "title": "Clean Code Python"},
    {"id": "7", "title": "Design Patterns"},
    {"id": "8", "title": "Database Systems"},
    {"id": "9", "title": "Cloud Computing Fundamentals"},
    {"id": "10", "title": "Software Architecture"}
]

@app.route("/books/<book_id>", methods=["GET"])
def find_by_id(book_id):
  for book in BOOKS:
    if book["id"] == book_id:
      return book
  return None

def get_book(book_id):
  book = find_by_id(book_id)
  if book is None:
    return jsonify({"error": "Book not found"}), 404
  return jsonify(book), 200

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
  return jsonify({"item": item_id}), 200

@app.route("/books", methods=["GET"])
def list_book():
  limit = int(request.args.get("limit", 3))
  q = request.args.get("q", "").strip().lower()
  items = [b for b in BOOKS if q in b["title"].lower()]
  return jsonify({"items": items[:limit]}), 200

if __name__ == "__main__":
  app.run(host="127.0.0.1",port=5000, debug=True)