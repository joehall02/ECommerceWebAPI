from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from models import User, Cart
from flask import Flask, current_app, request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from schemas import SignupSchema, LoginSchema
import jwt
import os

# Define the schema instances
signup_schema = SignupSchema()
login_schema = LoginSchema()

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
        

user_ns = Namespace('user', description='User operations')

# Define the models for the signup and login used for api
# documentation, actual validation is done using the schema
signup_model = user_ns.model('Signup', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'phone_number': fields.String(required=False),
})

login_model = user_ns.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@user_ns.route('/signup', methods=['POST'])
class SignupResource(Resource):
    def post(self):
        data = request.get_json()

        # Validate the request data against the signup schema
        try:
            valid_data = signup_schema.load(data)
        except ValidationError as e: # Return an error response if the request data is invalid
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        # Create a new user account
        try:
            UserService.create_user(valid_data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        return {'message': 'Account created successfully'}, 201

@user_ns.route('/login', methods=['POST'])
class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        # Validate the request data against the login schema
        try:
            valid_data = login_schema.load(data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Login the user
        try:
            access_token, refresh_token = UserService.login_user(valid_data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'access_token': access_token, 'refresh_token': refresh_token}, 200
    
@user_ns.route('/refresh', methods=['POST'])
class RefreshResource(Resource):
    @jwt_required(refresh=True) # Ensure that the token is a refresh token
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user_id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'access_token': new_access_token}, 200

@user_ns.route('/test', methods=['GET'])
class Test(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()        
        current_user = User.query.filter_by(id=current_user_id).first()
        if not current_user:
            return {'message': 'User not found'}, 404

        return {'message': 'Token is valid', 'user': current_user.email}, 200