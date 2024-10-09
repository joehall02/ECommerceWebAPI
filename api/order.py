from datetime import date
from marshmallow import ValidationError
from models import Order, OrderItem, Cart
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import get_jwt_identity, jwt_required
from schemas import OrderSchema, OrderItemSchema, OrderItemCombinedSchema
from decorators import admin_required

# Define the schema instances
order_schema = OrderSchema()
order_item_schema = OrderItemSchema()
order_item_combined_schema = OrderItemCombinedSchema()

# Services
class OrderService:
    @staticmethod
    def create_order(data):
        user = get_jwt_identity()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        # Get the cart
        cart = Cart.query.filter_by(user_id=user).first()

        # Get the cart items from the data
        cart_items = Cart.query.get(cart.id).cart_products

        # Check if the cart is empty
        if not cart_items:
            raise ValidationError('Cart is empty')

        # Create a new order
        new_order = Order(
            order_date = date.today(), # Get the current date in the format YYYY-MM-DD
            total_price = 0,
            status = 'Pending',
            user_id = user,
            address_id = data['address_id'],
            payment_id = data['payment_id']
        )
        new_order.save()

        # Loop through cart items and create an order item for each
        for cart_item in cart_items:
            new_order_item = OrderItem(
                quantity = cart_item.quantity,
                price = cart_item.product.price,
                product_id = cart_item.product_id,
                order_id = new_order.id
            )
            new_order_item.save()

            # Update the total price of the order
            new_order.total_price += new_order_item.price * new_order_item.quantity

        # Save the updated order
        new_order.save()

        return new_order
    
    @staticmethod
    def get_all_orders():
        user = get_jwt_identity()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        orders = Order.query.filter_by(user_id=user).all()

        # Check if there are any orders
        if not orders:
            raise ValidationError('No orders found')
        
        return orders
    
    @staticmethod
    def get_order(order_id):
        order = Order.query.get(order_id)
        
        # Check order exists
        if not order:
            raise ValidationError('Order not found')

        # Get the order items
        order_items = []

        for order_item in order.order_items:
            order_items.append(order_item)

        # Return the order and order items
        return {
            'order': order,
            'order_items': order_items
        }

    @staticmethod
    def get_all_customer_orders():
        orders = Order.query.all()

        # Check if there are any orders
        if not orders:
            raise ValidationError('No orders found')
        
        return orders
    
    @staticmethod
    def update_order_status(data, order_id):
        order = Order.query.get(order_id)

        # Check if the order exists
        if not order:
            raise ValidationError('Order not found')

        # Validate the data
        order_status = data['status']

        if order_status not in ['Processing', 'Shipped', 'Delivered']:
            raise ValidationError('Invalid order status')

        # Update the order status
        order.status = order_status
        order.save()

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
        
        try:
            orders = order_schema.dump(orders, many=True) # Serialize the data
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(orders, order_model), 200

    @jwt_required()
    def post(self): # Create an order and order items
        data = request.get_json()

        # Validate the data
        try:
            valid_data = order_schema.load(data, partial=True) # Partial allows for missing fields
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Create the order and order items
        try:
            OrderService.create_order(valid_data)
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
        
        try:
            order = order_item_combined_schema.dump(order)
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
        
        try:
            orders = order_schema.dump(orders, many=True)
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
            valid_data = order_schema.load(data, partial=True)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        try:
            OrderService.update_order_status(valid_data, order_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Order status updated successfully'}, 200
        
