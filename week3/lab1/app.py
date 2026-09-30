from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import BadRequest
app = Flask(__name__)
next_post_id = 1

POSTS = [
    {
        "id": 1,
        "title": "Getting Started with REST API",
        "content": "This post explains the basic concepts of REST and HTTP methods.",
        "author_id": 1,
        "tags": ["REST", "API", "HTTP"]
    },
    {
        "id": 2,
        "title": "Learning Flask",
        "content": "A simple introduction to building web APIs with Flask.",
        "author_id": 2,
        "tags": ["Flask", "Python", "Backend"]
    },
    {
        "id": 3,
        "title": "Understanding HTTP Status Codes",
        "content": "This post discusses common HTTP status codes such as 200, 201, 404 and 500.",
        "author_id": 1,
        "tags": ["HTTP", "REST", "Backend"]
    },
    {
        "id": 4,
        "title": "Docker for Backend Developers",
        "content": "An introduction to Docker and containerizing backend applications.",
        "author_id": 3,
        "tags": ["Docker", "Backend", "DevOps"]
    },
    {
        "id": 5,
        "title": "Introduction to Cloud Computing",
        "content": "This post introduces cloud computing concepts and common cloud services.",
        "author_id": 2,
        "tags": ["Cloud", "AWS", "DevOps"]
    },
    {
        "id": 6,
        "title": "REST API Best Practices",
        "content": "Some useful practices for designing clean and maintainable REST APIs.",
        "author_id": 1,
        "tags": ["REST", "API", "Backend"]
    }
]


@app.get("/api/v1/posts")
def list_posts():
    return jsonify({
        "data": POSTS,
        "total": len(POSTS)
    }), 200


@app.post("/api/v1/posts")
def create_post():
    global next_post_id

    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 415

    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({"error": "invalid JSON"}), 400

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    author_id = data.get("author_id")

    if not title or not content or author_id is None:
        return jsonify({"error": "missing title, content and author_id"}), 422

    post = {
        "id": next_post_id,
        "title": title,
        "content": content,
        "author_id": author_id,
        "tags": data.get("tags", [])
    }

    POSTS.append(post)
    next_post_id += 1

    response = make_response(jsonify(post), 201)
    response.headers["Location"] = (f"/api/v1/posts/{post['id']}")
    return response


if __name__ == "__main__":
  app.run(host="127.0.0.1",port=5000,debug=True)