from marshmallow import Schema, fields as ma_fields, ValidationError
from models import Order
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required

# Define the schema for the models used to validate the request data
class OrderSchema(Schema):
    order_date = ma_fields.DateTime(required=True, error_messages={'required': 'Order date is required', 'null': 'Order date cannot be empty'})
    total_price = ma_fields.Decimal(required=True, error_messages={'required': 'Total price is required', 'null': 'Total price cannot be empty'})
    status = ma_fields.String(required=True, error_messages={'required': 'Status is required', 'null': 'Status cannot be empty'})
    user_id = ma_fields.Integer(required=True, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})
    address_id = ma_fields.Integer(required=True, error_messages={'required': 'Address ID is required', 'null': 'Address ID cannot be empty'})
    payment_id = ma_fields.Integer(required=True, error_messages={'required': 'Payment ID is required', 'null': 'Payment ID cannot be empty'})


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
    
