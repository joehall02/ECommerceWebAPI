from flask_jwt_extended import create_access_token, create_refresh_token
from models import User, Cart
from flask import current_app
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

# Services
class UserService:
    @staticmethod
    def create_user(data):
        email_exists = User.query.filter_by(email=data['email']).first()
        phone_number_exists = None
        
        # Only check for phone number if it exists in the request data
        if 'phone_number' in data and data['phone_number']:
            phone_number_exists = User.query.filter_by(phone_number=data['phone_number']).first()
        
        # Check if a user with the provided email or phone number already exists
        if email_exists or phone_number_exists:
            raise ValidationError('User with the provided email or phone number already exists')

        # Check if there are any users in the database
        user_count = User.query.count()

        # Default role is customer
        role = "customer"

        # Check if the role is provided and is valid, only allow the first user to be an admin
        if 'role' in data and data['role']:
            if data['role'] == 'admin':
                if user_count == 0:
                    role = 'admin' # Allow first user to be an admin
                else:
                    raise ValidationError('Only the first user can be an admin')
            else:
                raise ValidationError('Invalid role')

        # Create a new user account
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=generate_password_hash(data['password']), # Generate a password hash before storing it
            email=data['email'],
            phone_number=data.get('phone_number', None), # Safely get the phone number from the request data or default to None
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
        user = User.query.filter_by(email=data['email']).first() # Get the user with the provided email
        
        if not user or not check_password_hash(user.password, data['password']): # Check if the user exists and the password is correct
            raise ValidationError('Invalid email or password')

        access_token = create_access_token(identity=user.id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create an access token for the user with a 1 hour expiry
        refresh_token = create_refresh_token(identity=user.id) # Create a refresh token for the user
        
        return access_token, refresh_token