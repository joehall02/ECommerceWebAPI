from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from models import User
from flask import Flask, current_app, request
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, fields as ma_fields, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import jwt
import os

# Define the schema for the signup and login operations used to validate the request data
class SignupSchema(Schema):
    first_name = ma_fields.String(required=True, error_messages={'required': 'First name is required', 'null': 'First name cannot be empty'})
    last_name = ma_fields.String(required=True, error_messages={'required': 'Last name is required', 'null': 'Last name cannot be empty'})
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    password = ma_fields.String(required=True, error_messages={'required': 'Password is required', 'null': 'Password cannot be empty'})
    phone_number = ma_fields.String(required=False, error_messages={'null': 'Phone number cannot be empty'})

class LoginSchema(Schema):
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    password = ma_fields.String(required=True, error_messages={'required': 'Password is required', 'null': 'Password cannot be empty'})

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

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=generate_password_hash(data['password']), # Generate a password hash before storing it
            email=data['email'],
            phone_number=data.get('phone_number', None), # Safely get the phone number from the request data or default to None
            role='customer'
        )
        new_user.save()
        return new_user
    
    @staticmethod
    def login_user(data):
        user = User.query.filter_by(email=data['email']).first() # Get the user with the provided email
        
        if not user or not check_password_hash(user.password, data['password']): # Check if the user exists and the password is correct
            raise ValidationError('Invalid email or password')

        access_token = create_access_token(identity=user.id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']) # Create an access token for the user with a 1 hour expiry
        refresh_token = create_refresh_token(identity=user.id) # Create a refresh token for the user
        
        return access_token, refresh_token
        

auth_ns = Namespace('auth', description='Authentication operations')

# Define the models for the signup and login used for api
# documentation, actual validation is done using the schema
signup_model = auth_ns.model('Signup', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'phone_number': fields.String(required=False),
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@auth_ns.route('/signup', methods=['POST'])
class SignupResource(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        data = request.get_json()

        # Validate the request data against the signup schema
        try:
            valid_data = signup_schema.load(data)
        except ValidationError as e: # Return an error response if the request data is invalid
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

        # Create a new user account
        try:
            UserService.create_user(valid_data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

        return {'message': 'Account created successfully'}, 201

@auth_ns.route('/login', methods=['POST'])
class LoginResource(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()

        # Validate the request data against the login schema
        try:
            valid_data = login_schema.load(data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        # Login the user
        try:
            access_token, refresh_token = UserService.login_user(valid_data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'access_token': access_token, 'refresh_token': refresh_token}, 200
    
@auth_ns.route('/refresh', methods=['POST'])
class RefreshResource(Resource):
    @jwt_required(refresh=True) # Ensure that the token is a refresh token
    def post(self):

        try:
            current_user_id = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user_id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'access_token': new_access_token}, 200

@auth_ns.route('/test', methods=['GET'])
class Test(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()        
        current_user = User.query.filter_by(id=current_user_id).first()
        if not current_user:
            return {'message': 'User not found'}, 404

        return {'message': 'Token is valid', 'user': current_user.email}, 200