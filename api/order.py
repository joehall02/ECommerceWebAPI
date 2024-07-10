from marshmallow import ValidationError
from models import Order
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from schemas import OrderSchema

# Define the schema instances
order_schema = OrderSchema()

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
    
