from flask_jwt_extended import create_access_token, create_refresh_token
from models import User, Cart
from flask import current_app
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
        phone_number_exists = None
        
        # Only check for phone number if it exists in the request data
        if 'phone_number' in valid_data and valid_data['phone_number']:
            phone_number_exists = User.query.filter_by(phone_number=valid_data['phone_number']).first()
        
        # Check if a user with the provided email or phone number already exists
        if email_exists or phone_number_exists:
            raise ValidationError('User with the provided email or phone number already exists')

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
            first_name=valid_data['first_name'],
            last_name=valid_data['last_name'],
            password=generate_password_hash(valid_data['password']), # Generate a password hash before storing it
            email=valid_data['email'],
            phone_number=valid_data.get('phone_number', None), # Safely get the phone number from the request data or default to None
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
        refresh_token = create_refresh_token(identity=user.id) # Create a refresh token for the user
        
        return access_token, refresh_token