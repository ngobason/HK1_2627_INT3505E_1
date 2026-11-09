import os
from flask import Flask, app

from .extensions import db, migrate
from .errors import register_error_handlers


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DB_URL", "sqlite:///products.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models
    from .api.products import products_bp
    app.register_blueprint(products_bp)
    from .api.orders import orders_bp
    app.register_blueprint(orders_bp)
    from .api.health import health_bp
    app.register_blueprint(health_bp)
    register_error_handlers(app)
    return app
