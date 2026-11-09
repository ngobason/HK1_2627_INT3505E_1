from marshmallow import Schema, fields, validate


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()


class ProductInSchema(Schema):
    sku = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=32)
    )

    name = fields.Str(
        required=True
    )

    price_cents = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )