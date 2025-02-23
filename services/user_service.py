from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies, get_csrf_token
from sqlalchemy import extract
from models import User, Cart, Order
from flask import current_app, make_response, jsonify
from marshmallow import ValidationError
from schemas import SignupSchema, LoginSchema
from werkzeug.security import generate_password_hash, check_password_hash
from exts import db

# Define the schema instances
signup_schema = SignupSchema()
login_schema = LoginSchema()    

# Services
class UserService:
    @staticmethod
    def create_user(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the signup schema
        valid_data = signup_schema.load(data)

        email_exists = User.query.filter_by(email=valid_data['email']).first()        
        
        # Check if a user with the provided email or phone number already exists
        if email_exists:
            raise ValidationError('User with the provided email already exists')

        # Check if there are any users in the database
        user_count = User.query.count()

        # Default role is customer
        role = "customer"

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
            created_at=datetime.now()
        )
        new_user.save()

        # Create a cart for the user
        new_cart = Cart(
            user_id=new_user.id
        )
        new_cart.save()

        return new_user
    
    @staticmethod
    def create_guest_user():
        # Create a new guest user account
        new_user = User(
            full_name='Guest User',
            password=generate_password_hash('guest'), # Generate a password hash before storing it
            role='guest',
            created_at=datetime.now()
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

        # Set the x-csrf-token header
        response.headers['x-access-csrf-token'] = get_csrf_token(access_token)
        response.headers['x-refresh-csrf-token'] = get_csrf_token(refresh_token)

        # Set HTTP-only cookies for the access and refresh tokens
        set_access_cookies(response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        set_refresh_cookies(response, refresh_token, max_age=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())

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

        access_token = create_access_token(identity=str(user.id), expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create an access token for the user with a 1 hour expiry
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']) # Create a refresh token for the user
        
        # Create a response
        response = make_response(jsonify({'message': 'Login successful'}))

        # Set the x-csrf-token header
        response.headers['x-access-csrf-token'] = get_csrf_token(access_token)
        response.headers['x-refresh-csrf-token'] = get_csrf_token(refresh_token)
        
        # Set HTTP-only cookies for the access and refresh tokens
        set_access_cookies(response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        set_refresh_cookies(response, refresh_token, max_age=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())

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

        access_token = create_access_token(identity=current_user_id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create a new access token

        response = make_response(jsonify(logged_in=logged_in, is_admin=is_admin, is_customer=is_customer))

        print("logged in: ", logged_in)
        print("is admin: ", is_admin)
        print("is customer:", is_customer)

        # Set the x-csrf-token header
        response.headers['x-access-csrf-token'] = get_csrf_token(access_token)

        # Set the new access token as an HTTP-only cookie
        set_access_cookies(response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())

        return response
        

    @staticmethod
    def refresh_token():
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create a new access token

        response = make_response(jsonify({'message': 'Token refreshed'}))

        # Set the x-csrf-token header
        response.headers['x-access-csrf-token'] = get_csrf_token(new_access_token)        

        # Set the new access token as an HTTP-only cookie
        set_access_cookies(response, new_access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())

        return response
    
    @staticmethod
    def reset_password(data):
        # Check if the data is provided
        if not data:
            raise ValidationError('No data provided')
        
        # Validate the request data against the login schema
        valid_data = login_schema.load(data)

        user = User.query.filter_by(email=valid_data['email']).first() # Get the user with the provided email

        if not user:
            raise ValidationError('User not found')
        
        # Update the user's password
        user.password = generate_password_hash(valid_data['password'])

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
        
        user.delete()

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
    def get_dashboard_data():
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
        current_year = datetime.now().year
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
