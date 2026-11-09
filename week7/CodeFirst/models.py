from extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    sku = db.Column(
        db.String(32),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    price_cents = db.Column(
        db.Integer,
        nullable=False
    )