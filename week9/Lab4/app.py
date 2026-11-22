from flask import Flask, request, jsonify
from gateway import dispatch

app = Flask(__name__)


@app.route("/orders", methods=["POST"])
def create_order():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    which, result = dispatch(body)

    response = jsonify(result)
    response.headers["X-Order-Handler"] = which

    return response, (201 if which == "v2" else 200)


if __name__ == "__main__":
    app.run(debug=True)
