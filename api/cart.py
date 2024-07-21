from marshmallow import ValidationError
from models import Cart, CartProduct, Product
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from schemas import CartSchema, CartProductSchema, ProductSchema

# Define the schema instances
cart_schema = CartSchema()
cart_product_schema = CartProductSchema()
product_schema = ProductSchema()

# Services
class CartService:
    pass

class CartProductService:
    pass

cart_ns = Namespace('cart', description='Cart operations')

# Define the models used for api documentation,
# actual validation is done using the schema
cart_model = cart_ns.model('Cart', {
    'user_id': fields.Integer(required=True),
})

cart_product_model = cart_ns.model('CartProduct', {
    'quantity': fields.Integer(required=True),
    'product_id': fields.Integer(required=True),
    'cart_id': fields.Integer(required=True),
})  

product_model = cart_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True),
    'category_id': fields.Integer(required=True),
})

# Define the routes for cart operations
@cart_ns.route('/', methods=['POST', 'GET'])
class CartResource(Resource):
    @jwt_required()
    def get(self):
        pass

    @jwt_required()
    def post(self):
        pass