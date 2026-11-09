from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, status, error, detail):
        self.status = status
        self.error = error
        self.detail = detail


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api(exc):
        return jsonify(error=exc.error, detail=exc.detail), exc.status

    @app.errorhandler(ValidationError)
    def handle_validation(exc):
        return jsonify(error="validation_error", detail=str(exc.messages)), 422

    @app.errorhandler(HTTPException)
    def handle_http(exc):
        return jsonify(error="http_error", detail=exc.description), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        app.logger.exception("Unhandled error")
        return jsonify(error="internal_error", detail="Internal server error"), 500
