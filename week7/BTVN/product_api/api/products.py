from flask import Blueprint, jsonify, request
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from ..errors import ApiError
from ..extensions import db
from ..models import Product
from ..schemas import ProductIn, ProductOut, ProductPatch, ReserveIn

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


def json_body():
    if not request.is_json:
        raise ApiError(400, "bad_request", "Content-Type must be application/json")
    try:
        body = request.get_json()
    except BadRequest:
        raise ApiError(400, "bad_request", "Invalid JSON") from None
    if not isinstance(body, dict):
        raise ApiError(422, "validation_error", "JSON object required")
    return body


def active_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        raise ApiError(404, "not_found", "Product not found")
    return product


@products_bp.get("")
def list_products():
    try:
        page = int(request.args.get("page", "1"))
        size = int(request.args.get("size", "20"))
    except ValueError:
        raise ApiError(422, "validation_error", "page and size must be integers") from None
    if page < 1 or not 1 <= size <= 100:
        raise ApiError(422, "validation_error", "page >= 1 and 1 <= size <= 100 required")

    base = db.select(Product).where(Product.archived.is_(False))
    rows = db.session.execute(
        base.order_by(Product.id).offset((page - 1) * size).limit(size)
    ).scalars().all()
    total = db.session.scalar(
        db.select(db.func.count()).select_from(Product).where(Product.archived.is_(False))
    )
    return jsonify(items=ProductOut(many=True).dump(rows), page=page, size=size, total=total), 200


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    return jsonify(ProductOut().dump(active_product(product_id))), 200


@products_bp.post("")
def create_product():
    data = ProductIn().load(json_body())
    product = Product(**data)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError(409, "conflict", "SKU already exists") from None
    return jsonify(ProductOut().dump(product)), 201, {"Location": f"/api/v1/products/{product.id}"}


@products_bp.patch("/<int:product_id>")
def update_product(product_id):
    data = ProductPatch().load(json_body())
    product = active_product(product_id)
    for field, value in data.items():
        setattr(product, field, value)
    db.session.commit()
    return jsonify(ProductOut().dump(product)), 200


@products_bp.post("/<int:product_id>/reserve")
def reserve_product(product_id):
    qty = ReserveIn().load(json_body())["qty"]
    result = db.session.execute(
        update(Product)
        .where(Product.id == product_id, Product.archived.is_(False), Product.qty_in_stock >= qty)
        .values(qty_in_stock=Product.qty_in_stock - qty)
    )
    if result.rowcount != 1:
        db.session.rollback()
        active_product(product_id)
        raise ApiError(409, "out_of_stock", "Insufficient stock")
    db.session.commit()
    return jsonify(ProductOut().dump(active_product(product_id))), 200


@products_bp.delete("/<int:product_id>")
def delete_product(product_id):
    product = active_product(product_id)
    product.archived = True
    db.session.commit()
    return "", 204
