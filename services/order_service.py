from datetime import date
from flask import jsonify, request
from marshmallow import ValidationError
from models import Order, OrderItem, Cart
from flask_jwt_extended import get_jwt_identity
from schemas import OrderSchema, OrderItemSchema, OrderItemCombinedSchema
import stripe

# Define the schema instances
order_schema = OrderSchema()
order_item_schema = OrderItemSchema()
order_item_combined_schema = OrderItemCombinedSchema()

# Services
class OrderService:
    @staticmethod
    def get_stripe_checkout_session(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the data against the order schema
        valid_data = order_schema.load(data, partial=True) # Partial allows for missing fields

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

        # Create line items for Stripe checkout session
        line_items = []
        for cart_item in cart_items:
            line_items.append({
                'price': cart_item.product.stripe_price_id, # Stripe price id
                'quantity': cart_item.quantity
            })

        # Create a stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:3000/checkout/success',
            cancel_url='http://localhost:3000/checkout/cancel',
            metadata={
                'user_id': user,
                'full_name': valid_data['full_name'],
                'address_line_1': valid_data['address_line_1'],
                'address_line_2': valid_data['address_line_2'] if 'address_line_2' in valid_data else None,
                'city': valid_data['city'],
                'postcode': valid_data['postcode'],
            }
        )

        return {'session_id': session.id}

    @staticmethod
    def create_order(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the data against the order schema
        valid_data = order_schema.load(data, partial=True) # Partial allows for missing fields

        user = valid_data['user_id'] 

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
            status = 'Processing', # Default status
            full_name = valid_data['full_name'],
            address_line_1 = valid_data['address_line_1'],
            address_line_2 = valid_data['address_line_2'],
            city = valid_data['city'],
            postcode = valid_data['postcode'],
            user_id = user,
        )
        new_order.save()

        # Loop through cart items and create an order item for each
        for cart_item in cart_items:
            new_order_item = OrderItem(
                quantity = cart_item.quantity,
                name = cart_item.product.name,
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
        
        # Serialize the data
        orders = order_schema.dump(orders, many=True)
    
        return orders
    
    @staticmethod
    def get_order(order_id):
        # Check if the order id is provided
        if not order_id:
            raise ValidationError('No order id provided')

        order = Order.query.get(order_id)
        
        # Check order exists
        if not order:
            raise ValidationError('Order not found')

        # Get the order items
        order_items = []

        for order_item in order.order_items:
            order_items.append(order_item)

        order = {
            'order': order,
            'order_items': order_items
        }

        # Serialize the data
        order = order_item_combined_schema.dump(order)        

        # Return the order and order items
        return order

    @staticmethod
    def get_all_customer_orders():
        orders = Order.query.all()

        # Check if there are any orders
        if not orders:
            raise ValidationError('No orders found')
        
        # Serialize the data
        orders = order_schema.dump(orders, many=True)
        
        return orders
    
    @staticmethod
    def update_order_status(data, order_id):
        # Check if the order id is provided
        if not order_id:
            raise ValidationError('No order id provided')

        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the data against the order schema
        valid_data = order_schema.load(data, partial=True)

        order = Order.query.get(order_id)

        # Check if the order exists
        if not order:
            raise ValidationError('Order not found')

        # Validate the data
        order_status = valid_data['status']

        if order_status not in ['Processing', 'Shipped', 'Delivered']:
            raise ValidationError('Invalid order status')

        # Update the order status
        order.status = order_status
        order.save()


        