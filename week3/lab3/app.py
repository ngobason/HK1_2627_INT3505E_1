from flask import Flask, jsonify, request
import base64
import json

app = Flask(__name__)

ORDERS = [
    {"id": 1, "customer_id": "C001", "status": "paid", "total": 120, "created_at": "2026-10-01T09:00:00"},
    {"id": 2, "customer_id": "C002", "status": "pending", "total": 80, "created_at": "2026-10-01T10:00:00"},
    {"id": 3, "customer_id": "C001", "status": "paid", "total": 250, "created_at": "2026-10-01T11:00:00"},
    {"id": 4, "customer_id": "C003", "status": "cancelled", "total": 60, "created_at": "2026-10-01T12:00:00"},
    {"id": 5, "customer_id": "C002", "status": "paid", "total": 180, "created_at": "2026-10-01T13:00:00"},
    {"id": 6, "customer_id": "C004", "status": "pending", "total": 90, "created_at": "2026-10-01T14:00:00"},
    {"id": 7, "customer_id": "C001", "status": "paid", "total": 310, "created_at": "2026-10-01T15:00:00"},
    {"id": 8, "customer_id": "C003", "status": "paid", "total": 150, "created_at": "2026-10-01T16:00:00"},
    {"id": 9, "customer_id": "C004", "status": "pending", "total": 220, "created_at": "2026-10-01T17:00:00"},
    {"id": 10, "customer_id": "C002", "status": "paid", "total": 100, "created_at": "2026-10-01T18:00:00"},
]


def encode_cursor(data):
    raw = json.dumps(data).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor):
    try:
        padding = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(cursor + padding)
        return json.loads(raw.decode())
    except Exception:
        raise ValueError("Invalid cursor")


@app.get("/orders")
def get_orders():
    # -------------------------
    # 1. limit
    # -------------------------
    try:
        limit = int(request.args.get("limit", 3))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    if limit < 1:
        return jsonify({"error": "limit must be greater than 0"}), 400

    limit = min(limit, 100)

    # -------------------------
    # 2. filter
    # -------------------------
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")

    result = ORDERS

    if status:
        result = [
            order for order in result
            if order["status"] == status
        ]

    if customer_id:
        result = [
            order for order in result
            if order["customer_id"] == customer_id
        ]

    # -------------------------
    # 3. sort
    # -------------------------
    sort = request.args.get("sort", "id")

    descending = sort.startswith("-")

    sort_field = sort[1:] if descending else sort

    allowed_sort_fields = {
        "id",
        "total",
        "created_at"
    }

    if sort_field not in allowed_sort_fields:
        return jsonify({"error": "Invalid sort field"}), 400

    result = sorted(
        result,
        key=lambda order: (
            order[sort_field],
            order["id"]
        ),
        reverse=descending
    )

    # -------------------------
    # 4. cursor
    # -------------------------
    cursor = request.args.get("cursor")

    if cursor:
        try:
            cursor_data = decode_cursor(cursor)

            if cursor_data["sort"] != sort:
                return jsonify({
                    "error": "Cursor does not match current sort"
                }), 400

            last_value = cursor_data["last_value"]
            last_id = cursor_data["last_id"]

        except (ValueError, KeyError, TypeError):
            return jsonify({"error": "Invalid cursor"}), 400

        if descending:
            result = [
                order for order in result
                if (
                    order[sort_field],
                    order["id"]
                ) < (
                    last_value,
                    last_id
                )
            ]
        else:
            result = [
                order for order in result
                if (
                    order[sort_field],
                    order["id"]
                ) > (
                    last_value,
                    last_id
                )
            ]

    page = result[:limit]

    next_cursor = None

    if len(result) > limit:
        last_order = page[-1]

        next_cursor = encode_cursor({
            "sort": sort,
            "last_value": last_order[sort_field],
            "last_id": last_order["id"]
        })

    # -------------------------
    # 5. sparse fieldsets
    # -------------------------
    fields_param = request.args.get("fields")

    if fields_param:
        fields = [
            field.strip()
            for field in fields_param.split(",")
        ]

        allowed_fields = {
            "id",
            "customer_id",
            "status",
            "total",
            "created_at"
        }

        for field in fields:
            if field not in allowed_fields:
                return jsonify({
                    "error": f"Invalid field: {field}"
                }), 400

        page = [
            {
                field: order[field]
                for field in fields
            }
            for order in page
        ]

    return jsonify({
        "data": page,
        "next_cursor": next_cursor
    }), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)