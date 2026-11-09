from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..errors import ApiError
from ..models import Order, OrderItem, Product
from ..schemas import OrderIn, OrderOut

orders_bp = Blueprint(
    "orders", __name__, url_prefix="/api/v1/orders"
)


@orders_bp.post("")
def create_order():
    if not request.is_json:
        raise ApiError(400, "bad_request", "JSON required")

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Invalid JSON")

    data = OrderIn().load(body)
    order = Order(status="pending")

    for item in data["items"]:
        product = db.session.get(Product, item["product_id"])

        if product is None or product.archived:
            raise ApiError(404, "not_found", "Product not found")

        order.items.append(OrderItem(
            product=product,
            qty=item["qty"],
            unit_price_cents=product.price_cents
        ))

    db.session.add(order)
    db.session.commit()

    return jsonify(OrderOut().dump(order)), 201


@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    order = db.session.execute(
        db.select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .where(Order.id == order_id)
    ).scalar_one_or_none()

    if order is None:
        raise ApiError(404, "not_found", "Order not found")

    return jsonify(OrderOut().dump(order)), 200