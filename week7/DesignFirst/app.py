import connexion
from models import db

app = connexion.FlaskApp(
    __name__,
    specification_dir="openapi/"
)

flask_app = app.app

flask_app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///products.db"
)

db.init_app(flask_app)

with flask_app.app_context():
    db.create_all()

app.add_api("products.yaml")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)