from datetime import datetime
from marshmallow import ValidationError
from models import Order, OrderItem, Cart, ProductImage, Product, User
from flask_jwt_extended import get_jwt_identity
from schemas import OrderSchema, OrderItemSchema, OrderItemCombinedSchema, OrderAdminSchema, OrderItemCombinedAdminSchema
import stripe
from flask import current_app
from services.utils import send_email, create_stripe_checkout_session
from services.product_service import ProductService, FeaturedProductService
from services.user_service import UserService
from exts import cache

# Define the schema instances
order_schema = OrderSchema()
order_item_schema = OrderItemSchema()
order_item_combined_schema = OrderItemCombinedSchema()
order_admin_schema = OrderAdminSchema()
order_item_combined_admin_schema = OrderItemCombinedAdminSchema()

# Services
class OrderService:
    @staticmethod
    def get_stripe_checkout_session(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the data against the order schema
        valid_data = order_schema.load(data, partial=True) # Partial allows for missing fields

        # Check that an address is provided by checking if the strings are empty
        if not valid_data['full_name'] or not valid_data['address_line_1'] or not valid_data['city'] or not valid_data['postcode']:
            raise ValidationError('Address not provided')

        user_id = get_jwt_identity()

        # Get the user
        user = User.query.get(user_id)

        # Check if the user exists
        if not user_id:
            raise ValidationError('User not found')

        # Get the cart
        cart = Cart.query.filter_by(user_id=user_id).first()

        # Get the cart items from the data
        cart_items = Cart.query.get(cart.id).cart_products

        # Check if the cart is empty
        if not cart_items:
            raise ValidationError('Cart is empty')

        # Lock the cart
        cart.locked = True
        cart.locked_at = datetime.now()
        cart.save()

        # Create line items for Stripe checkout session
        line_items = []
        for cart_item in cart_items:
            # Check the stock of the product
            if cart_item.product.stock < cart_item.quantity:
                raise ValidationError(cart_item.product.name + ' only has ' + str(cart_item.product.stock) + ' left in stock')
            elif cart_item.product.reserved_stock < cart_item.quantity:
                raise ValidationError(cart_item.product.name + ' only has ' + str(cart_item.product.stock - cart_item.product.reserved_stock) + ' left in stock')
            
            line_items.append({
                'price': cart_item.product.stripe_price_id, # Stripe price id
                'quantity': cart_item.quantity
            })

        # Create a stripe checkout session
        session = create_stripe_checkout_session(user, valid_data, line_items)

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
            order_date = datetime.now(), # Get the current date in the format YYYY-MM-DD
            total_price = 0,
            status = 'Processing', # Default status
            full_name = valid_data['full_name'],
            address_line_1 = valid_data['address_line_1'],
            address_line_2 = valid_data['address_line_2'],
            city = valid_data['city'],
            postcode = valid_data['postcode'],
            customer_email = valid_data['customer_email'],
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

            # Delete the cart item
            cart_item.delete()

            # Update the product stock
            product = Product.query.get(cart_item.product_id)

            product.stock -= new_order_item.quantity
            # product.reserved_stock -= new_order_item.quantity
            product.reserved_stock = max(product.reserved_stock - new_order_item.quantity, 0) # Ensure reserved stock doesn't go negative
            product.save()

            # Update the total price of the order
            new_order.total_price += new_order_item.price * new_order_item.quantity

        # Save the updated order
        new_order.save()

        # Unlock the cart
        cart.locked = False
        cart.locked_at = None
        cart.product_added_at = None
        cart.save()

        # Clear the cache for the products
        cache.delete_memoized(ProductService.get_all_products) 
        cache.delete_memoized(ProductService.get_all_admin_products)
        cache.delete_memoized(FeaturedProductService.get_all_featured_products)
        cache.delete_memoized(UserService.get_dashboard_data)
        cache.delete_memoized(OrderService.get_all_customer_orders)
        cache.delete_memoized(OrderService.get_all_of_a_users_orders)

        return new_order
    
    @staticmethod
    def get_all_orders(page=1, per_page=6):        
        user = get_jwt_identity()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        # Get the orders for the user, order by order date in descending order, i.e. latest order first
        query = Order.query.filter_by(user_id=user).order_by(Order.order_date.desc()) 
        orders_query = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = orders_query.items

        # Check if there are any orders
        if not orders:
            raise ValidationError('No orders found')
        
        entire_order = []

        # Get the order items for each order
        for order in orders:
            order_items = []

            for order_item in order.order_items:

                # Get the product image
                product_image = ProductImage.query.filter_by(product_id=order_item.product_id).first()

                if product_image:
                    order_item.product_image = product_image.image_path                

                order_items.append(order_item)

            entire_order.append({
                'order': order,
                'order_items': order_items
            })
        
        # Serialize the data
        orders = order_item_combined_schema.dump(entire_order, many=True)
    
        return {
            'orders': orders,
            'total_pages': orders_query.pages,
            'current_page': orders_query.page,
            'total_orders': orders_query.total
        }
    
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
            # Get the product image
            product_image = ProductImage.query.filter_by(product_id=order_item.product_id).first()

            if product_image:
                order_item.product_image = product_image.image_path
            
            order_items.append(order_item)

        # Get customer name and email if user exists
        if order.user:
            customer = order.user

            order = {
                'order': order,
                'order_items': order_items,
                'customer_name': customer.full_name,
            }

            # Serialize the data
            order = order_item_combined_admin_schema.dump(order)        

            # Return the order and order items
            return order
        else:
            order = {
                'order': order,
                'order_items': order_items
            }

            # Serialize the data
            order = order_item_combined_admin_schema.dump(order)        

            # Return the order and order items
            return order       

    @staticmethod
    @cache.memoize(timeout=86400) # Cache for 24 hours
    def get_all_customer_orders(page=1, per_page=10, status=None):
        print('Fetching customer orders')
        # Apply sorting
        if status == 'Processing':
            query = Order.query.filter_by(status='Processing').order_by(Order.id.desc()) 
        elif status == 'Shipped':
            query = Order.query.filter_by(status='Shipped').order_by(Order.id.desc())
        elif status == 'Delivered':
            query = Order.query.filter_by(status='Delivered').order_by(Order.id.desc())
        else:
            query = Order.query.order_by(Order.id.desc())


        orders_query = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = orders_query.items

        # Check if there are any orders
        if not orders:
            raise ValidationError('No orders found')
        
        # Serialize the data
        orders = order_admin_schema.dump(orders, many=True)
        
        return {
            'orders': orders,
            'total_pages': orders_query.pages,
            'current_page': orders_query.page,
            'total_orders': orders_query.total
        }
    
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

        # Get the order status
        order_status = valid_data['status']

        if order_status not in ['Processing', 'Shipped', 'Delivered']:
            raise ValidationError('Invalid order status')

        if order_status == 'Shipped':
            # Send an email to the customer
            email_data = {
                'to_name': order.full_name,
                'to_email': order.customer_email,
                'subject': 'Order Shipped',
                'text': 'Your order has been shipped! You will receive another email with the tracking number soon.'
            }
            send_email(email_data)

        # Update the order status
        order.status = order_status
        order.save()

        # Clear the cache
        cache.delete_memoized(UserService.get_dashboard_data)
        cache.delete_memoized(OrderService.get_all_customer_orders)
        cache.delete_memoized(OrderService.get_all_of_a_users_orders)

        return order

    @staticmethod
    @cache.memoize(timeout=86400) # Cache for 24 hours
    def get_all_of_a_users_orders(page=1, per_page=6, user_id=None):
        print('Fetching user orders')
        # Check if the user id is provided
        if not user_id:
            raise ValidationError('No user id provided')

        # Check if the user exists
        if not User.query.get(user_id):
            raise ValidationError('User not found')

        # Get the orders for the user, order by order date in descending order, i.e. latest order first
        query = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()) 
        orders_query = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = orders_query.items        
        
        entire_order = []

        # Get the order items for each order
        for order in orders:
            order_items = []

            for order_item in order.order_items:

                # Get the product image
                product_image = ProductImage.query.filter_by(product_id=order_item.product_id).first()

                if product_image:
                    order_item.product_image = product_image.image_path                

                order_items.append(order_item)

            entire_order.append({
                'order': order,
                'order_items': order_items
            })
        
        # Serialize the data
        orders = order_item_combined_schema.dump(entire_order, many=True)
    
        return {
            'orders': orders,
            'total_pages': orders_query.pages,
            'current_page': orders_query.page,
            'total_orders': orders_query.total
        }

         

        