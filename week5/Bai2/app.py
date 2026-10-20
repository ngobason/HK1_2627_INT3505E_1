from pathlib import Path

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from models import db
from routes.common import APIError
from routes.books import bp as books_bp
from routes.authors import bp as authors_bp
from routes.categories import bp as categories_bp
from routes.users import bp as users_bp
from routes.reviews import bp as reviews_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///bookstore.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.json.ensure_ascii = False
    db.init_app(app)

    for blueprint in (
        books_bp,
        authors_bp,
        categories_bp,
        users_bp,
        reviews_bp,
    ):
        app.register_blueprint(blueprint, url_prefix="/api/v1")

    @app.get("/")
    def index():
        return jsonify(
            message="Bookstore API - Bài 2: Flask pagination",
            endpoints={
                "books": "/api/v1/books",
                "authors": "/api/v1/authors",
                "categories": "/api/v1/categories",
                "users": "/api/v1/users",
                "reviews": "/api/v1/reviews",
            },
        )

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify(error=error.message), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error=error.description), error.code

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
