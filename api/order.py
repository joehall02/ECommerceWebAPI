from marshmallow import ValidationError
from models import Order
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from schemas import OrderSchema, OrderItemSchema

# Define the schema instances
order_schema = OrderSchema()
order_item_schema = OrderItemSchema()

# Services
class OrderService:
    pass

class OrderItemService:
    pass

order_ns = Namespace('order', description='Administrator operations')

# Define the models used for api documentation,
# actual validation is done using the schema
order_model = order_ns.model('Order', {
    'order_date': fields.DateTime(required=True),
    'total_price': fields.Float(required=True),
    'status': fields.String(required=True),
    'user_id': fields.Integer(required=True),
    'address_id': fields.Integer(required=True),
    'payment_id': fields.Integer(required=True),
})
    
order_item_model = order_ns.model('OrderItem', {
    'quantity': fields.Integer(required=True),
    'price': fields.Float(required=True),
    'product_id': fields.Integer(required=True),
    'order_id': fields.Integer(required=True),
})

# Define the routes for order operations
@order_ns.route('/', methods=['POST', 'GET'])
class OrderResource(Resource):
    @jwt_required()
    def get(self): # Get all orders
        pass

    @jwt_required()
    def post(self): # Create an order and order items
        pass

@order_ns.route('/<int:order_id>', methods=['GET', 'PUT', 'DELETE'])
class OrderResource(Resource):
    @jwt_required()
    def get(self, order_id): # Get an order and its order items
        pass

@order_ns.route('/admin', methods=['GET', 'PUT'])
class AdminOrderResource(Resource):
    @jwt_required()
    def get(self): # Get all customer orders
        pass

    @jwt_required()
    def put(self): # Change the status of a customer order
        pass
