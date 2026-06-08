import graphene
from graphene import ObjectType, String, Int
from stocks.schemas.product import Product
from db import get_redis_conn
from db import get_sqlalchemy_session
from stocks.models.product import Product as ProductModel

class Query(ObjectType):       
    product = graphene.Field(Product, id=String(required=True))
    stock_level = Int(product_id=String(required=True))
    
    def resolve_product(self, info, id):
        redis_client = get_redis_conn()

        product_data = redis_client.hgetall(f"stock:{id}")

        if not product_data:
            return None

        session = get_sqlalchemy_session()

        try:
            product = (
                session.query(ProductModel)
                .filter(ProductModel.id == int(id))
                .first()
            )

            if not product:
                return None

            return Product(
                id=int(id),
                name=product_data["name"],
                sku=product_data["sku"],
                price=float(product_data["price"]),
                quantity=int(product_data["quantity"])
            )

        finally:
            session.close()
    
    def resolve_stock_level(self, info, product_id):
        """ Retrieve stock quantity from Redis """
        redis_client = get_redis_conn()
        quantity = redis_client.hget(f"stock:{product_id}", "quantity")
        return int(quantity) if quantity else 0