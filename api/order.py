from marshmallow import ValidationError
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from decorators import admin_required
from services.order_service import OrderService

order_ns = Namespace('order', description='Administrator operations')

# Define the models used for api documentation,
# actual validation is done using the schema
order_model = order_ns.model('Order', {
    'order_date': fields.Date(required=True),
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

combined_model = order_ns.model('Combined', {
    'order': fields.Nested(order_model),
    'order_items': fields.List(fields.Nested(order_item_model)),
})

# Define the routes for order operations
@order_ns.route('/', methods=['POST', 'GET'])
class OrderResource(Resource):
    @jwt_required()
    def get(self): # Get all orders
        try:
            orders = OrderService.get_all_orders()
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(orders, order_model), 200

    @jwt_required()
    def post(self): # Create an order and order items
        data = request.get_json()
        
        # Create the order and order items
        try:
            OrderService.create_order(data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
            
        return {'message': 'Order created successfully'}, 201

@order_ns.route('/<int:order_id>', methods=['GET'])
class OrderResource(Resource):
    @jwt_required()
    def get(self, order_id): # Get an order and its order items
        try:
            order = OrderService.get_order(order_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(order, combined_model), 200

@order_ns.route('/admin', methods=['GET'])
class AdminOrderResource(Resource):
    @jwt_required()
    @admin_required()
    def get(self): # Get all customer orders
        try:
            orders = OrderService.get_all_customer_orders()
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500    
        
        return marshal(orders, order_model), 200

@order_ns.route('/admin/<int:order_id>', methods=['PUT'])
class AdminOrderResource(Resource):  
    @jwt_required()
    @admin_required()
    def put(self, order_id): # Change the status of a customer order
        data = request.get_json()

        try:
            OrderService.update_order_status(data, order_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Order status updated successfully'}, 200
        
