import sqlite3
import hashlib
import json
from flask import Flask, jsonify, request, make_response
app = Flask(__name__)
DATABASE = "books.db"

def get_db():
  conn = sqlite3.connect(DATABASE)
  conn.row_factory = sqlite3.Row
  return conn

def init_db():
  conn = get_db()

  conn.execute("""
      CREATE TABLE IF NOT EXISTS books (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          author TEXT NOT NULL,
          isbn TEXT,
          price REAL
      )
  """)
  conn.commit()
  conn.close()



#Tra danh sach
@app.get("/books")
def list_book():
    conn = get_db()
    rows = conn.execute("SELECT * FROM books").fetchall()

    conn.close()

    books = [dict(row) for row in rows]
    return jsonify({
        "data": books,
        "total": len(books)
    }), 200



#Tao sach moi
@app.post("/books")
def create_book():
  if not request.is_json:
    return jsonify({"error": "expected JSON"}), 415
  data = request.get_json(silent=True) or {}
  t, a = (data.get("title") or "").strip(), (data.get("author") or "").strip()
  if not t or not a:
    return jsonify({"error": "must have title and author"}), 422
  conn = get_db()

  cursor = conn.execute(
      """
      INSERT INTO books (title, author, isbn, price)
      VALUES (?, ?, ?, ?)
      """,
      (
          t,
          a,
          data.get("isbn"),
          data.get("price")
      )
  )
  conn.commit()

  book_id = cursor.lastrowid
  book = {
    "id": book_id,
    "title": t,
    "author": a,
    "isbn": data.get("isbn"),
    "price": data.get("price")
  }

  conn.close()

  resp = make_response(jsonify({"data": book}), 201)
  resp.headers["Location"] = f"/books/{book_id}"
  return resp



# Lay book theo id và ETag
@app.get("/books/<int:book_id>")
def get_book(book_id):
    conn = get_db()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify({"error": "Book not found"}), 404
    
    book = dict(row)
    book_json = json.dumps(book, sort_keys=True)

    etag = hashlib.md5(
        book_json.encode()
    ).hexdigest()

    etag = f'"{etag}"'
    client_etag = request.headers.get("If-None-Match")

    if client_etag == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        return resp

    resp = make_response(jsonify(book), 200)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "max-age=60"
    return resp



#Thay toan bo title + author
@app.put("/books/<int:book_id>")
def modify_book(book_id):
  conn = get_db()

  row = conn.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
  if row is None:
      conn.close()
      return jsonify({"error": "Book not found"}), 404

  new_data = request.get_json(silent=True) or {}

  t = (new_data.get("title") or "").strip()
  a = (new_data.get("author") or "").strip()

  if not t or not a:
      conn.close()
      return jsonify({"error": "Must have title and author"}), 422

  conn.execute(
    """
    UPDATE books
    SET title = ?, author = ?, isbn = ?, price = ?
    WHERE id = ?
    """,
    (
        t,
        a,
        new_data.get("isbn"),
        new_data.get("price"),
        book_id
    )
  )

  conn.commit()

  updated = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
  conn.close()

  return jsonify(dict(updated)), 200



#Cap nhat 1 phan thong tin sach
@app.patch("/books/<int:book_id>")
def patch(book_id):
  conn = get_db()

  row = conn.execute(
      "SELECT * FROM books WHERE id = ?",
      (book_id,)
  ).fetchone()

  if row is None:
    conn.close()
    return jsonify({"error": "Book not found"}), 404

  book = dict(row)
  data = request.get_json(silent=True) or {}
  if "price" in data and data["price"] is not None and data["price"] < 0:
    conn.close()
    return jsonify({"error": "Price must be positive"}), 422
  for field in ["title", "author", "isbn", "price"]:
    if field in data:
        book[field] = data[field]

  conn.execute(
    """
    UPDATE books
    SET title = ?, author = ?, isbn = ?, price = ?
    WHERE id = ?
    """,
    (
        book["title"],
        book["author"],
        book["isbn"],
        book["price"],
        book_id
    )
  )

  conn.commit()
  conn.close()
  return jsonify(book), 200



#Xoa sach
@app.delete("/books/<int:book_id>")
def delete_book(book_id):
  conn = get_db()

  row = conn.execute(
      "SELECT id FROM books WHERE id = ?",
      (book_id,)
  ).fetchone()

  if row is None:
      conn.close()
      return jsonify({"error": "Book not found"}), 404

  conn.execute(
    "DELETE FROM books WHERE id = ?",
    (book_id,)
)

  conn.commit()
  conn.close()
  return "", 204



if __name__ == "__main__":
  init_db()
  app.run(host="127.0.0.1", port=5000, debug=True)