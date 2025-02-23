from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
from models import User
from flask import current_app, request, jsonify
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from services.user_service import UserService   
from decorators import handle_exceptions, admin_required, customer_required

user_ns = Namespace('user', description='User operations')

# Define the models for the signup and login used for api
# documentation, actual validation is done using the schema
signup_model = user_ns.model('Signup', {
    'full_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'stripe_customer_id': fields.String(required=False),
})

login_model = user_ns.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@user_ns.route('/signup', methods=['POST'])
class SignupResource(Resource):
    @handle_exceptions
    def post(self): # Create a new user account
        data = request.get_json()

        UserService.create_user(data)

        return {'message': 'Account created successfully'}, 201

@user_ns.route('/login', methods=['POST'])
class LoginResource(Resource):
    @handle_exceptions
    def post(self): # Login a user
        data = request.get_json()

        response = UserService.login_user(data)
        
        return response
    
@user_ns.route('/authenticate', methods=['GET'])
class AuthenticatedResource(Resource):
    @jwt_required() # Ensure that the user is authenticated
    @handle_exceptions
    def get(self): # Authenticate the user
        response = UserService.authenticate_user()

        return response
    
@user_ns.route('/logout', methods=['POST'])
class LogoutResource(Resource):
    @handle_exceptions
    def post(self):
        response = jsonify({'message': 'Logout successful'})
        unset_jwt_cookies(response) # Unset the jwt cookies, effectively logging the user out
        return response
    
@user_ns.route('/reset-password', methods=['PUT'])
class ResetPasswordResource(Resource):
    @jwt_required()
    @handle_exceptions
    def put(self): # Reset the user password
        data = request.get_json()
        
        UserService.reset_password(data)    
        
        return {'message': 'Password reset successfully'}, 200
    
@user_ns.route('/edit-name', methods=['PUT'])
class EditNameResource(Resource):
    @jwt_required()
    @customer_required()
    @handle_exceptions
    def put(self): # Change the users name
        data = request.get_json()

        UserService.edit_name(data)

        return {'message': 'Name edited successfully'}, 200

@user_ns.route('/edit-password', methods=['PUT'])
class EditPasswordResource(Resource):
    @jwt_required()
    @customer_required()
    @handle_exceptions
    def put(self): # Change the users password
        data = request.get_json()

        UserService.edit_password(data)

        return {'message': 'Password edited successfully'}, 200

@user_ns.route('/delete-account', methods=['DELETE'])
class DeleteAccountResource(Resource):
    @jwt_required()
    @customer_required()
    @handle_exceptions
    def delete(self): # Delete the users account
        UserService.delete_account()

        return {'message': 'Account deleted successfully'}, 200


@user_ns.route('/refresh', methods=['POST'])
class RefreshResource(Resource):
    @jwt_required(refresh=True) # Ensure that the user is authenticated
    @handle_exceptions
    def post(self): # Refresh the access token                        
        response = UserService.refresh_token()

        return response                
    
@user_ns.route('/', methods=['GET'])
class UserResource(Resource):
    @jwt_required()
    @customer_required()
    @handle_exceptions
    def get(self): # Get the user's name
        response = UserService.get_full_name()

        return response
    
@user_ns.route('/admin', methods=['GET'])
class AdminResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self):
        results = UserService.get_dashboard_data()

        response = {
            'total_users': results['total_users'],
            'ongoing_orders': results['ongoing_orders'],
            'orders_overall': results['orders_overall'],
            'total_revenue': results['total_revenue'],
            'graph_data': results['graph_data']
        }

        return response, 200
