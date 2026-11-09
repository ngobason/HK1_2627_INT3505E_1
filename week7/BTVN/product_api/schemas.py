from marshmallow import Schema, fields, validate


class ProductOut(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()


class ProductIn(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(required=True, strict=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))


class ProductPatch(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(strict=True, validate=validate.Range(min=0))


class ReserveIn(Schema):
    qty = fields.Int(required=True, strict=True, validate=validate.Range(min=1))

class OrderItemIn(Schema):
    product_id = fields.Int(required=True, strict=True)
    qty = fields.Int(
        required=True, strict=True,
        validate=validate.Range(min=1)
    )


class OrderIn(Schema):
    items = fields.List(
        fields.Nested(OrderItemIn),
        required=True,
        validate=validate.Length(min=1)
    )


class OrderItemOut(Schema):
    product_id = fields.Int()
    product_name = fields.Function(lambda item: item.product.name)
    qty = fields.Int()
    unit_price_cents = fields.Int()


class OrderOut(Schema):
    id = fields.Int()
    status = fields.Str()
    created_at = fields.DateTime()
    items = fields.Nested(OrderItemOut, many=True)