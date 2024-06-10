from models import User
from flask import Flask, request
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, fields as ma_fields, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import jwt
import os

# Define the schema for the signup and login operations used to validate the request data
class SignupSchema(Schema):
    first_name = ma_fields.String(required=True)
    last_name = ma_fields.String(required=True)
    email = ma_fields.Email(required=True)
    password = ma_fields.String(required=True)
    phone_number = ma_fields.String(required=False)

class LoginSchema(Schema):
    email = ma_fields.Email(required=True)
    password = ma_fields.String(required=True)

# Define the schema instances
signup_schema = SignupSchema()
login_schema = LoginSchema()

# Services
class UserService:
    @staticmethod
    def create_user(data):
        email_exists = User.query.filter_by(email=data['email']).first()
        phone_number_exists = User.query.filter_by(phone_number=data['phone_number']).first()
        if email_exists or phone_number_exists:
            raise ValidationError('User with the provided email or phone number already exists')

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=generate_password_hash(data['password']), # Generate a password hash before storing it
            email=data['email'],
            phone_number=data['phone_number'],
            role='customer'
        )
        new_user.save()
        return new_user
    
    @staticmethod
    def login_user(data):
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']): # Check if the user exists and the password is correct
            raise ValidationError('Invalid email or password')
        
        token = jwt.encode({
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1) # Set the token to expire in 1 hour
        },
        os.getenv('SECRET_KEY'),
        'HS256'
        )
        
        return token
        

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
    'email': fields.String(),
    'password': fields.String()
})

@auth_ns.route('/signup', methods=['POST'])
class Signup(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        data = request.get_json()

        # Validate the request data against the signup schema
        try:
            valid_data = signup_schema.load(data)
        except ValidationError as e: # Return an error response if the request data is invalid
            return {'message': str(e)}, 400

        # Create a new user account
        try:
            UserService.create_user(valid_data)
        except ValidationError as e:
            return {'message': str(e)}, 400

        return {'message': 'Account created successfully'}, 201

@auth_ns.route('/login', methods=['POST'])
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()

        # Validate the request data against the login schema
        try:
            valid_data = login_schema.load(data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        
        # Login the user
        try:
            token = UserService.login_user(valid_data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        
        return {'token': token}, 200
    
