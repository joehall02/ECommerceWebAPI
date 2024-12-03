from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
from models import User
from flask import current_app, request, jsonify
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from services.user_service import UserService   
from decorators import handle_exceptions 

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
    def get(self):
        try:
            current_user_id = get_jwt_identity() 
            if not current_user_id:
                logged_in = False
            else:
                logged_in = True
                       
        except Exception as e:
            return {'error': str(e)}, 500
        
        return jsonify(logged_in=logged_in)
    
@user_ns.route('/logout', methods=['POST'])
class LogoutResource(Resource):
    def post(self):
        response = jsonify({'message': 'Logout successful'})
        unset_jwt_cookies(response)
        return response
    
@user_ns.route('/reset-password', methods=['PUT'])
class ResetPasswordResource(Resource):
    @handle_exceptions
    def put(self): # Reset the user password
        data = request.get_json()
        
        UserService.reset_password(data)    
        
        return {'message': 'Password reset successfully'}, 200
    
# @user_ns.route('/refresh', methods=['POST'])
# class RefreshResource(Resource):
#     @jwt_required(refresh=True) # Ensure that the token is a refresh token
#     def post(self): # Refresh the access token
#         try:
#             current_user_id = get_jwt_identity()
#             new_access_token = create_access_token(identity=current_user_id, expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
#         except ValidationError as e:
#             return {'error': str(e)}, 400
#         except Exception as e:
#             return {'error': str(e)}, 500
        
#         return {'access_token': new_access_token}, 200