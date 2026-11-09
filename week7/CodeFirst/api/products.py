from flask.views import MethodView
from flask_smorest import Blueprint

from extensions import db
from models import Product
from schemas import ProductSchema, ProductInSchema


blp = Blueprint(
    "products",
    __name__,
    url_prefix="/products"
)


class ProductList(MethodView):

    # POST /products
    @blp.arguments(ProductInSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):

        product = Product(**data)

        db.session.add(product)
        db.session.commit()

        return product

    # GET /products
    @blp.response(200, ProductSchema(many=True))
    def get(self):

        return db.session.execute(
            db.select(Product)
        ).scalars().all()


blp.add_url_rule(
    "",
    view_func=ProductList.as_view("product_list")
)