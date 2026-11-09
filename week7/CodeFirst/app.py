from flask import Flask
from flask_smorest import Api

from extensions import db
from api.products import blp


app = Flask(__name__)

app.config.update({
    "API_TITLE": "Product API",
    "API_VERSION": "1.0.0",
    "OPENAPI_VERSION": "3.0.3",

    "OPENAPI_URL_PREFIX": "/",
    "OPENAPI_SWAGGER_UI_PATH": "/swagger-ui",
    "OPENAPI_SWAGGER_UI_URL":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/",

    "SQLALCHEMY_DATABASE_URI":
        "sqlite:///products.db",

    "SQLALCHEMY_TRACK_MODIFICATIONS": False
})

db.init_app(app)

api = Api(app)
api.register_blueprint(blp)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(port=5000, debug=True)