from models import db, Product


def list_products():
    products = db.session.execute(
        db.select(Product)
    ).scalars().all()

    return [p.to_dict() for p in products], 200


def create_product(body):
    p = Product(**body)

    db.session.add(p)
    db.session.commit()

    return p.to_dict(), 201


def get_product(id):
    p = db.session.get(Product, id)

    if p is None:
        return {"message": "Not found"}, 404

    return p.to_dict(), 200