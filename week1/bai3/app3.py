from flask import Flask, jsonify, request
from uuid import uuid4
app = Flask(__name__)
STUDENT = []
@app.route("/students", methods=["POST"])

def students():
  data = request.get_json(silent=True) or {}
  name = data.get("name")
  if not name:
    return jsonify({"error": "must have name"}), 400
  student = {
    "id": str(uuid4()),
    "name": name,
    "gpa": data.get("gpa", 0.0)
  }
  STUDENT.append(student)
  response = jsonify(student)
  response.status_code = 201
  response.headers["Location"] = f"/students/{student['id']}"
  return response

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)