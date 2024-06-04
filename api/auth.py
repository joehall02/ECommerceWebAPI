from models import User
from flask import Flask, request
from flask_restx import Namespace, Resource, fields

auth_ns = Namespace('auth', description='Authentication operations')

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

        email_exists = User.query.filter_by(email=data['email']).first()
        if email_exists:
            return {'message': f'An account with that email already exists'}, 400

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
            email=data['email'],
            phone_number=data['phone_number'],
            role='customer'
        )
        new_user.save()

        return {'message': 'Account created successfully'}, 201
    