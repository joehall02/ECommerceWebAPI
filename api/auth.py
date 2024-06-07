from models import User
from flask import Flask, request
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, fields, ValidationError

# Define the schema for the signup and login operations used to validate the request data
class SignupSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    phone_number = fields.Str(required=False)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

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
            password=data['password'],
            email=data['email'],
            phone_number=data['phone_number'],
            role='customer'
        )
        new_user.save()
        return new_user
    
    def login(data):
        pass
    

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
    'username': fields.String(),
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
