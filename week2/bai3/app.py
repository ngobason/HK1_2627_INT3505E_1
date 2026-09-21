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
    },
    {
        "id": 6,
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "isbn": "9781593279288",
        "price": 24.99
    },
    {
        "id": 7,
        "title": "Learning JavaScript",
        "author": "Ethan Brown",
        "isbn": "9781491914915",
        "price": 26.50
    },
    {
        "id": 8,
        "title": "Node.js in Action",
        "author": "Mike Cantelon",
        "isbn": "9781617292576",
        "price": 28.00
    },
    {
        "id": 9,
        "title": "Cloud Computing",
        "author": "Thomas Erl",
        "isbn": "9780133387520",
        "price": 32.99
    },
    {
        "id": 10,
        "title": "Software Architecture in Practice",
        "author": "Len Bass",
        "isbn": "9780136886099",
        "price": 39.99
    }
]

DEFAULT_SIZE = 3
MAX_SIZE = 100

@app.get("/books")
def get_books():
  try:
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", DEFAULT_SIZE))
  except ValueError:
    return jsonify({"error": "page and size must be int"}), 400
  # Lay page va size
  page = max(page, 1)
  size = max(1, min(size, MAX_SIZE))

  # Filtering
  filtered_books = BOOKS
  author = request.args.get("author")
  if author:
    filtered_books = [book for book in filtered_books if book["author"].lower() == author.lower()]
  q = (request.args.get("q") or "").lower()

  if q:
        filtered_books = [book for book in filtered_books if q in book["title"].lower()]

  # Pagination
  total = len(filtered_books)
  total_pages = (total + size - 1) // size
  start = (page - 1) * size
  end = start + size

  items = filtered_books[start:end]

  # HATEOAS links
  def url(page_number):
    return f"/books?page={page_number}&size={size}"

  links = {
      "self": {
          "href": url(page)
      },
      "first": {
          "href": url(1)
      },
      "last": {
          "href": url(max(total_pages, 1))
      }
  }

  if page > 1:
    links["prev"] = {"href": url(page - 1)}

  if page < total_pages:
    links["next"] = {"href": url(page + 1)}

  body = {
    "data": items,
    "pagination": {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": total_pages
    },
    "_links": links
  }

    # Cache-Control
  response = make_response(jsonify(body), 200)
  response.headers["Cache-Control"] = "public, max-age=30"
  return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)