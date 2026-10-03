from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import HTTPException
app = Flask(__name__)



RESOURCES = [
    {"id": 1, "name": "Resource 1"},
    {"id": 2, "name": "Resource 2"}
]


class ProblemError(Exception):
    def __init__(self, status, title, detail, type="about:blank"):
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type


def problem_json(status, title, detail, type="about:blank"):
    body = {
        "type": type,
        "title": title,
        "detail": detail,
        "status": status,
        "instance": request.path
    }

    response = make_response(jsonify(body), status)
    response.headers["Content-Type"] = "application/problem+json"
    return response


# Handler cho ProblemError
@app.errorhandler(ProblemError)
def handle_problem_error(error):
    return problem_json(
        error.status,
        error.title,
        error.detail,
        error.type
    )


# Fallback cho lỗi HTTP của Flask
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    return problem_json(
        error.code,
        error.name,
        error.description
    )


@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error("Unhandled exception", exc_info=True)

    return problem_json(
        500,
        "Internal Server Error",
        "An unexpected error occurred"
    )


@app.get("/resources/<int:resource_id>")
def get_resource(resource_id):
    resource = next((r for r in RESOURCES if r["id"] == resource_id), None)

    if resource is None:
        raise ProblemError(
            404,
            "Not Found",
            "Resource not found"
        )

    return jsonify(resource), 200

@app.get("/test-500")
def test_500():
    raise RuntimeError("Test unexpected error")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)