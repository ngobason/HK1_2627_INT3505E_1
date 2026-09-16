from flask import Flask, jsonify, request, make_response
app = Flask(__name__)
BOOKS = []
next_id = 1

#Tra danh sach
@app.get("/books")
def list_book():
  return jsonify({
    "data": BOOKS,
    "total": len(BOOKS)
  }), 200

#Tao sach moi
@app.post("/books")
def create_book():
  global next_id
  if not request.is_json:
    return jsonify({"error": "expected JSON"}), 415
  data = request.get_json(silent=True) or {}
  t, a = (data.get("title") or "").strip(), (data.get("author") or "").strip()
  if not t or not a:
    return jsonify({"error": "must have title and author"}), 422
  book = {
    "id": next_id,
    "title": t,
    "author": a
  }
  BOOKS.append(book)
  next_id += 1
  resp = make_response(jsonify({"data": book}), 201)
  resp.headers["Location"] = f"/books/{book['id']}"
  return resp

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)