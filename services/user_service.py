from datetime import datetime
from zoneinfo import ZoneInfo
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies
from sqlalchemy import extract
from models import Product, User, Cart, Order
from flask import current_app, make_response, jsonify
from marshmallow import ValidationError
from schemas import SignupSchema, LoginSchema, UserSchema, UserAdminSchema
from werkzeug.security import generate_password_hash, check_password_hash
from exts import db, cache
from services.product_service import ProductService
from services.utils import send_email, generate_verification_token, verify_token, send_contact_us_email, convert_utc_to_uk_time
from dateutil.parser import parse


# Define the schema instances
signup_schema = SignupSchema()
login_schema = LoginSchema()    
user_admin_schema = UserAdminSchema()
user_schema = UserSchema()

# Services
class UserService:
    @staticmethod
    def create_user(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the signup schema
        valid_data = signup_schema.load(data)

        # Check the length of the password
        if (len(valid_data['password']) < 8):
            raise ValidationError('Password must be at least 8 characters long')

        email_exists = User.query.filter_by(email=valid_data['email']).first()        
        
        # Check if a user with the provided email or phone number already exists
        if email_exists:
            raise ValidationError('User with the provided email already exists')

        # Check if there are any users in the database
        user_count = User.query.count()

        # Default role is customer
        role = "customer"

        # If there are no users, set the role to admin
        if user_count == 0:
            role = 'admin'

        # Check if the role is provided and is valid, only allow the first user to be an admin
        if 'role' in valid_data and valid_data['role']:
            if valid_data['role'] == 'admin':
                if user_count == 0:
                    role = 'admin' # Allow first user to be an admin
                else:
                    raise ValidationError('Only the first user can be an admin')
            else:
                raise ValidationError('Invalid role')

        # Create a new user account
        new_user = User(
            full_name=valid_data['full_name'],
            password=generate_password_hash(valid_data['password']), # Generate a password hash before storing it
            email=valid_data['email'],
            role=role,
            created_at=datetime.now(tz=ZoneInfo("UTC")),
            is_verified=False,
            verification_token=generate_verification_token(valid_data['email'])
        )
        new_user.save()

        # Create a cart for the user
        new_cart = Cart(
            user_id=new_user.id
        )
        new_cart.save()

        # Send verification email
        verification_link = f"{current_app.config['FRONTEND_PUBLIC_URL']}/login/{new_user.verification_token}"
        email_data = {
            'to_name': new_user.full_name,
            'to_email': new_user.email,
            'subject': 'Verify your email address',
            'text': f'Click the link to verify your email address: {verification_link}'
        }
        
        # Clear the cache
        cache.delete_memoized(UserService.get_all_admin_users)
        cache.delete_memoized(UserService.get_dashboard_data)
        
        # Send the verification email
        try:
            send_email(email_data)
        except Exception as e:
            new_user.delete() # Delete the user if the email fails to send
            raise ValidationError('Failed to send verification email. Please try again later.')

        new_user.last_verification_email_sent = datetime.now(tz=ZoneInfo("UTC"))
        new_user.save()


        return new_user
    
    @staticmethod
    def verify_email(token):
        # Check if the token is provided
        if not token:
            raise ValidationError('No token provided')
        
        # Verify the token
        email = verify_token(token)

        # Check if the returned value is provided
        if not email:
            raise ValidationError('Token invalid or expired')

        # Get the user with the provided email
        user = User.query.filter_by(email=email).first()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')
        
        # Check if the token matches the user's verification token
        if user.verification_token != token:
            raise ValidationError('Invalid token or expired')

        # Check if the user is already verified
        if user.is_verified:
            raise ValidationError('Account already verified')

        # Verify the user
        user.is_verified = True
        user.verification_token = None # Remove the verification token after the user is verified
        user.save()

        return user
    
    @staticmethod
    def resend_verification_email(data):
        # Check if the data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the login schema
        try:
            valid_data = login_schema.load(data, partial=True)
        except ValidationError as e:
            raise ValidationError('Invalid email provided')

        # Get the user with the provided email
        user = User.query.filter_by(email=valid_data['email']).first()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')
        
        # Check if the user is already verified
        if user.is_verified:
            raise ValidationError('Email already verified')
        
        # Check if the user has requested a resend recently (less than 60 seconds)
        if user.last_verification_email_sent and (datetime.now(tz=ZoneInfo("UTC")) - user.last_verification_email_sent).seconds < 60:
            raise ValidationError('Please wait before requesting another verification email')

        # Generate a new verification token
        user.verification_token = generate_verification_token(user.email)
        user.save()

        # Send verification email
        verification_link = f"{current_app.config['FRONTEND_PUBLIC_URL']}/login/{user.verification_token}"
        email_data = {
            'to_name': user.full_name,
            'to_email': user.email,
            'subject': 'Verify your email address',
            'text': f'Click the link to verify your email address: {verification_link}'
        }

        send_email(email_data)

        user.last_verification_email_sent = datetime.now(tz=ZoneInfo("UTC"))
        user.save()

        return user

    @staticmethod
    def create_guest_user():
        # Create a new guest user account
        new_user = User(
            full_name='Guest User',
            password=generate_password_hash('guest'), # Generate a password hash before storing it
            role='guest',
            created_at=datetime.now(tz=ZoneInfo("UTC"))
        )
        new_user.save()

        # Create a cart for the user
        new_cart = Cart(
            user_id=new_user.id
        )

        new_cart.save()

        # Create am access token for the guest user
        access_token = create_access_token(identity=str(new_user.id), expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create an access token for the user with a 1 hour expiry
        refresh_token = create_refresh_token(identity=str(new_user.id), expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']) # Create a refresh token for the user

        # Create a response
        response = make_response(jsonify({'message': 'Guest user created', 'access_token': access_token, 'refresh_token': refresh_token}))

        # Clear the cache
        cache.delete_memoized(UserService.get_all_admin_users)
        cache.delete_memoized(UserService.get_dashboard_data)

        return new_user.id, response

    @staticmethod
    def login_user(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the login schema
        valid_data = login_schema.load(data)

        user = User.query.filter_by(email=valid_data['email']).first() # Get the user with the provided email
        
        if not user or not check_password_hash(user.password, valid_data['password']): # Check if the user exists and the password is correct
            raise ValidationError('Invalid email or password')
        
        if not user.is_verified:
            raise ValidationError('Email not verified')

        access_token = create_access_token(identity=str(user.id), expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create an access token for the user with a 1 hour expiry
        
        if valid_data['remember_me'] == True:
            refresh_token = create_refresh_token(identity=str(user.id), expires_delta=current_app.config['JWT_REFRESH_TOKEN_REMEMBER_ME_EXPIRES'])
        else:
            refresh_token = create_refresh_token(identity=str(user.id), expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']) 
        
        # Create a response
        response = make_response(jsonify({'message': 'Login successful'}))
        
        # Set HTTP-only cookies for the access and refresh tokens
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response

    @staticmethod
    def authenticate_user():
        current_user_id = get_jwt_identity() 
        if not current_user_id:
            logged_in = False
            is_admin = False
            is_customer = False
        else:
            logged_in = True

            # Check if the user is an admin
            user = User.query.get(current_user_id)
            if user.role == 'admin':
                is_admin = True
                is_customer = False
            elif user.role == 'customer':
                is_customer = True
                is_admin = False
            else:
                is_admin = False
                is_customer = False

        response = make_response(jsonify(logged_in=logged_in, is_admin=is_admin, is_customer=is_customer))

        print("logged in: ", logged_in)
        print("is admin: ", is_admin)
        print("is customer:", is_customer)

        return response
        
    @staticmethod
    def refresh_token():
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create a new access token

        response = make_response(jsonify({'message': 'Token refreshed'}))     

        # Set the new access token as an HTTP-only cookie
        set_access_cookies(response, new_access_token)

        return response
    
    @staticmethod
    def send_password_reset_email(data):
        # Check if the data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the login schema
        valid_data = login_schema.load(data, partial=True)

        # Get the user with the provided email
        user = User.query.filter_by(email=valid_data['email']).first()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        # Check if the user has requested a reset password email recently (less than 60 seconds)
        if user.last_verification_email_sent and (datetime.now(tz=ZoneInfo("UTC")) - user.last_verification_email_sent).seconds < 60:
            raise ValidationError('Please wait before requesting another reset password email')
        
        # Generate a new verification token 
        user.verification_token = generate_verification_token(user.email)
        user.save()

        # Send verification email
        reset_password_link = f"{current_app.config['FRONTEND_PUBLIC_URL']}/reset-password/{user.verification_token}"
        email_data = {
            'to_name': user.full_name,
            'to_email': user.email,
            'subject': 'Reset your password',
            'text': f'Click the link to reset your password: {reset_password_link}'
        }

        try:
            send_email(email_data)
        except Exception as e:
            raise ValidationError('Failed to send reset password email. Please try again later.')

        user.last_verification_email_sent = datetime.now(tz=ZoneInfo("UTC"))
        user.save()

        return user

    @staticmethod
    def reset_password(token, data):
        # Check if the token is provided
        if not token:
            raise ValidationError('No token provided')

        # Check if the data is provided
        if not data:
            raise ValidationError('No data provided')

        # Verify the token
        email = verify_token(token)

        # Check if the returned value is provided
        if not email:
            raise ValidationError('Token invalid or expired')

        # Check the length of the new password
        if (len(data['new_password']) < 8):
            raise ValidationError('Password must be at least 8 characters long')

        # Get the user with the provided email
        user = User.query.filter_by(email=email).first()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        # Check if the token matches the user's verification token
        if user.verification_token != token:
            raise ValidationError('Invalid token or expired')

        # Update the user's password
        user.password = generate_password_hash(data['new_password'])

        user.verification_token = None # Remove the verification token after the user resets their password
        user.save()

        return user
    
    @staticmethod
    def edit_name(data):
        # Check if the data is provided
        if not data:
            raise ValidationError('No data provided')
        
        # Validate the request data against the sign up schema
        valid_data = signup_schema.load(data, partial=True)

        # Get current user
        current_user_id = get_jwt_identity()

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            raise ValidationError('User not found')
        
        # Update the users name
        user.full_name = valid_data['full_name']

        user.save()

        # Clear the cache
        cache.delete_memoized(UserService.get_all_admin_users)

        return user

    @staticmethod
    def delete_account():
        # Get current user
        current_user_id = get_jwt_identity()

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            raise ValidationError('User not found')
        
        # If the user has an orders that are not delivered, do not allow the user to delete their account
        if user.orders:
            for order in user.orders:
                if order.status != 'Delivered':
                    raise ValidationError('Cannot delete account with pending orders')
        
        # Check if the user has cart items, if so, remove the reserved stock
        cart = Cart.query.filter_by(user_id=user.id).first()
        if cart:
            cart_products = cart.cart_products

            if cart_products:
                for cart_product in cart_products:
                    product = Product.query.get(cart_product.product_id)
                    if product:
                        # product.reserved_stock -= cart_product.quantity
                        product.reserved_stock = max(product.reserved_stock - cart_product.quantity, 0) # Ensure stock doesn't go negative
                        product.save()

        user.delete()

        # Clear the cache
        cache.delete_memoized(UserService.get_all_admin_users)
        cache.delete_memoized(UserService.get_dashboard_data)
        cache.delete_memoized(ProductService.get_all_products)

        return user
        
    @staticmethod
    def get_full_name():
        # Get current user
        current_user_id = get_jwt_identity()

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            raise ValidationError('User not found')
        
        return {'full_name': user.full_name}
    
    @staticmethod
    def edit_password(data):
        # Check if the data is provided
        if not data:
            raise ValidationError('No data provided')
        
        # Check the length of the new password
        if (len(data['new_password']) < 8):
            raise ValidationError('Password must be at least 8 characters long')

        # Get current user
        current_user_id = get_jwt_identity()

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            raise ValidationError('User not found')
        
        # Check if the current password is correct
        if not check_password_hash(user.password, data['current_password']):
            raise ValidationError('Current password invalid')
        
        # Update the users password
        user.password = generate_password_hash(data['new_password'])

        user.save()

        return user
    
    @staticmethod
    @cache.memoize(timeout=86400) # Cache for 24 hours
    def get_dashboard_data():
        print('Fetching dashboard data')
        # Get current user
        current_user_id = get_jwt_identity()

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            raise ValidationError('User not found')
        
        # Get the total number of users
        total_users = User.query.count()

        # Get the total number of ongoing orders
        ongoing_orders = Order.query.filter(Order.status.in_(['Processing', 'Shipped'])).count()

        # Get the total number of orders
        orders_overall = Order.query.count()

        # Get the total revenue from all orders
        total_revenue = Order.query.with_entities(Order.total_price).all()
        total_revenue = sum(float(revenue[0]) for revenue in total_revenue)
        total_revenue = round(total_revenue, 2) # Round the total revenue to 2 decimal places

        # Get the number of orders per month for the current year
        current_year = datetime.now(tz=ZoneInfo("UTC")).year
        orders_per_month = (
            db.session.query(
                extract('month', Order.order_date).label('month'),
                db.func.count(Order.id).label('order_count')
            )
            .filter(extract('year', Order.order_date) == current_year)
            .group_by('month')
            .order_by('month')
            .all()
        )

        orders_per_month_data = {month: 0 for month in range(1, 13)}
        for month, order_count in orders_per_month:
            orders_per_month_data[month] = order_count

        return {
            'total_users': total_users,
            'ongoing_orders': ongoing_orders,
            'orders_overall': orders_overall,
            'total_revenue': total_revenue,
            'graph_data': orders_per_month_data
        }
    
    # @staticmethod
    # def delete_old_guest_users():
    #     expiration_date = datetime.now(tz=ZoneInfo("UTC")) - timedelta(days=7)
        
    #     print("Deleting guest users")

    #     # Get all guest users that are older than expiration date
    #     guest_users = User.query.filter(User.role == 'guest', User.created_at < expiration_date).all()

    #     if not guest_users:
    #         raise ValidationError('No guest users, older than 7 days old, found')

    #     for guest_user in guest_users:
    #         # Check if the guest user has any cart items, if so, remove the reserved stock
    #         cart = Cart.query.filter_by(user_id=guest_user.id).first()
    #         if cart:                
    #             cart_products = cart.cart_products

    #             if cart_products:
    #                 for cart_product in cart_products:
    #                     product = Product.query.get(cart_product.product_id)
    #                     if product:
    #                         # product.reserved_stock -= cart_product.quantity
    #                         product.reserved_stock = max(product.reserved_stock - cart_product.quantity, 0) # Ensure stock doesn't go negative
    #                         product.save()

    #         guest_user.delete()

    #     # Clear the cache
    #     cache.delete_memoized(UserService.get_all_admin_users)
    #     cache.delete_memoized(UserService.get_dashboard_data)           
    #     cache.delete_memoized(ProductService.get_all_products)

    #     return {'message': 'Old guest users deleted'}
        
        
    @staticmethod
    @cache.memoize(timeout=86400) # Cache for 24 hours
    def get_all_admin_users(page):
        print('Fetching admin users')
        query = User.query.order_by(User.created_at.desc()) # Get all users ordered by the date they were created

        # Paginate the results
        users_query = query.paginate(page=page, per_page=10)
        users = users_query.items

        if not users:
            raise ValidationError('No users found')
        
        # Serialise the users
        users = user_admin_schema.dump(users, many=True)

        return {
            'users': users,
            'total_pages': users_query.pages,
            'current_page': users_query.page,
            'total_users': users_query.total
        }

    @staticmethod
    def get_user(user_id):
        # Check if the user id is provided
        if not user_id:
            raise ValidationError('No user id provided')
        
        user = User.query.get(user_id)

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')
                
        # Serialise the user
        user = user_schema.dump(user)

        if user['created_at']:
            # Convert utc datetime to local datetime
            user['created_at'] = convert_utc_to_uk_time(parse(user['created_at'])).isoformat()   

        return user
    
    @staticmethod
    def send_contact_us_email(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        response = send_contact_us_email(data)
        
        return response