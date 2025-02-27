from marshmallow import ValidationError
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from decorators import admin_required
from services.order_service import OrderService
from decorators import handle_exceptions, customer_required
from models import User
import stripe

order_ns = Namespace('order', description='Administrator operations')

# Define the models used for api documentation,
# actual validation is done using the schema
order_model = order_ns.model('Order', {
    'id': fields.Integer(required=True),
    'order_date': fields.Date(required=True),
    'total_price': fields.Float(required=True),
    'status': fields.String(required=True),
    'full_name': fields.String(required=True),
    'address_line_1': fields.String(required=True),
    'address_line_2': fields.String(),
    'city': fields.String(required=True),
    'postcode': fields.String(required=True),
    'customer_email': fields.String(required=True),
    'user_id': fields.Integer(required=True),    
})
    
order_item_model = order_ns.model('OrderItem', {
    'quantity': fields.Integer(required=True),
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'product_image': fields.String(), # This field is not required
    'product_id': fields.Integer(), # This field is not required, if product is deleted product_id is set to null
    'order_id': fields.Integer(required=True),
})

order_admin_model = order_ns.model('OrderAdmin', {
    'id': fields.Integer(required=True),
    'order_date': fields.Date(required=True),
    'total_price': fields.Float(required=True),
    'status': fields.String(required=True),
    'full_name': fields.String(required=True),
})

combined_model = order_ns.model('Combined', {
    'order': fields.Nested(order_model),
    'order_items': fields.List(fields.Nested(order_item_model)),
})

combined_admin_model = order_ns.model('CombinedAdmin', {
    'order': fields.Nested(order_model),
    'order_items': fields.List(fields.Nested(order_item_model)),
    'customer_name': fields.String(required=True),
})

# Define the routes for order operations
@order_ns.route('/', methods=['GET'])
class OrderResource(Resource):
    @jwt_required()
    @customer_required()
    @handle_exceptions
    def get(self): # Get all orders        
        page = request.args.get('page', 1, type=int) # Get the page number from the query string        

        results = OrderService.get_all_orders(page)        
        
        response = {
            'orders': marshal(results['orders'], combined_model),
            'total_pages': results['total_pages'],
            'current_page': results['current_page'],
            'total_orders': results['total_orders']
        }

        return response, 200

@order_ns.route('/checkout', methods=['POST'])
class OrderResource(Resource):
    @jwt_required()
    @handle_exceptions
    def post(self): # Create an order and order items
        data = request.get_json()
                
        # Returns stripe checkout session url
        checkout_session = OrderService.get_stripe_checkout_session(data) 

        return {'session_id': checkout_session['session_id']}, 200

@order_ns.route('/admin', methods=['GET'])
class AdminOrderResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self): # Get all customer orders        
        page = request.args.get('page', 1, type=int) # Get the page number from the query string
        status = request.args.get('status', type=str) # Get the status from the query string

        results = OrderService.get_all_customer_orders(page, per_page=10, status=status)        
        
        response = {
            'orders': marshal(results['orders'], order_admin_model),
            'total_pages': results['total_pages'],
            'current_page': results['current_page'],
            'total_orders': results['total_orders']
        }

        return response, 200

@order_ns.route('/admin/<int:order_id>', methods=['PUT', 'GET'])
class AdminOrderResource(Resource):  
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self, order_id): # Get an order, its order items and customer details
        order = OrderService.get_order(order_id)        
        
        return marshal(order, combined_admin_model), 200

    @jwt_required()
    @admin_required()
    @handle_exceptions
    def put(self, order_id): # Change the status of a customer order
        data = request.get_json()
        
        OrderService.update_order_status(data, order_id)        
        
        return {'message': 'Order status updated successfully'}, 200
    
@order_ns.route('/admin/user/<int:user_id>', methods=['GET'])
class AdminOrderResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self, user_id): # Get all orders for a user
        page = request.args.get('page', 1, type=int) # Get the page number from the query string

        results = OrderService.get_all_of_a_users_orders(page, per_page=6, user_id=user_id)

        response = {
            'orders': marshal(results['orders'], combined_model),
            'total_pages': results['total_pages'],
            'current_page': results['current_page'],
            'total_orders': results['total_orders']
        }

        return response, 200
    
@order_ns.route('/webhook', methods=['POST'])
class OrderResource(Resource):
    def post(self): # Handle stripe webhook
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe.webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            return {'error': str(e)}, 400
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return {'error': str(e)}, 400
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object'] # Contains a stripe checkout session            
            customer_email = session['customer_details']['email']

            # Extract the metadata, which contains the user id and address details
            metadata = session['metadata']
            user_id = metadata['user_id']
            full_name = metadata['full_name']
            address_line_1 = metadata['address_line_1']
            address_line_2 = metadata['address_line_2']
            city = metadata['city']
            postcode = metadata['postcode']

            
            # Create a new order
            data = {
                'user_id': user_id,
                'full_name': full_name,
                'address_line_1': address_line_1,
                'address_line_2': address_line_2,
                'city': city,
                'postcode': postcode,
                'customer_email': customer_email
            }

            # Extract the stripe customer id
            stripe_customer_id = session['customer']

            user = User.query.get(user_id)

            if user:
                user.stripe_customer_id = stripe_customer_id
                user.save()
                
            OrderService.create_order(data)
            
        return {'message': 'Webhook received'}, 200