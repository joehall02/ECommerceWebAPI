from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies, get_csrf_token
from models import User, Cart
from flask import current_app, make_response, jsonify
from marshmallow import ValidationError
from schemas import SignupSchema, LoginSchema
from werkzeug.security import generate_password_hash, check_password_hash

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
            role=role
        )
        new_user.save()

        # Create a cart for the user
        new_cart = Cart(
            user_id=new_user.id
        )
        new_cart.save()

        return new_user
    
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

        access_token = create_access_token(identity=user.id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create an access token for the user with a 1 hour expiry
        refresh_token = create_refresh_token(identity=user.id, expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']) # Create a refresh token for the user
        
        # Create a response
        response = make_response(jsonify({'message': 'Login successful'}))

        # Set the x-csrf-token header
        response.headers['x-access-csrf-token'] = get_csrf_token(access_token)
        response.headers['x-refresh-csrf-token'] = get_csrf_token(refresh_token)

        # response.set_cookie('access_token', access_token, httponly=True, secure=False, samesite='Lax', path='/')
        # response.set_cookie('refresh_token', refresh_token, httponly=True, secure=False, samesite='Lax', path='/')
        
        # Set HTTP-only cookies for the access and refresh tokens
        set_access_cookies(response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        set_refresh_cookies(response, refresh_token, max_age=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())

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