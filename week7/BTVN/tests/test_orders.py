import pytest
from product_api import create_app
from product_api.extensions import db
from product_api.models import Product
from sqlalchemy import event


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        products = [
            Product(
                sku="TEST-001", name="Ban phim",
                price_cents=250000, qty_in_stock=10
            ),
            Product(
                sku="TEST-002", name="Chuot",
                price_cents=150000, qty_in_stock=20
            )
        ]

        db.session.add_all(products)
        db.session.commit()

        ids = [p.id for p in products]
        yield app.test_client(), ids

        db.session.remove()
        db.drop_all()


def test_create_order(client):
    api, ids = client

    response = api.post("/api/v1/orders", json={
        "items": [
            {"product_id": ids[0], "qty": 2},
            {"product_id": ids[1], "qty": 1}
        ]
    })

    assert response.status_code == 201

    data = response.get_json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 2
    assert data["items"][0]["qty"] == 2
    assert data["items"][0]["unit_price_cents"] == 250000
    assert data["items"][1]["qty"] == 1
    assert data["items"][1]["unit_price_cents"] == 150000

def test_get_order_eager_loading(client):
    api, ids = client

    created = api.post("/api/v1/orders", json={
        "items": [
            {"product_id": ids[0], "qty": 2},
            {"product_id": ids[1], "qty": 1}
        ]
    })
    assert created.status_code == 201

    order_id = created.get_json()["id"]
    db.session.remove()

    queries = []

    def count_queries(conn, cursor, statement, params, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    event.listen(db.engine, "before_cursor_execute", count_queries)

    try:
        response = api.get(f"/api/v1/orders/{order_id}")
    finally:
        event.remove(db.engine, "before_cursor_execute", count_queries)

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["items"]) == 2
    assert {item["product_name"] for item in data["items"]} == {
        "Ban phim", "Chuot"
    }

    assert len(queries) <= 3, f"N+1 detected: {len(queries)} queries"