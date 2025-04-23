from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields, marshal
from services.user_service import UserService   
from decorators import handle_exceptions, admin_required, customer_required
from exts import limiter

user_ns = Namespace('user', description='User operations')

# Define the models for the signup and login used for api
# documentation, actual validation is done using the schema
user_model = user_ns.model('User', {
    'id': fields.Integer(required=True),
    'full_name': fields.String(required=True),
    'email': fields.String(required=True),
    'stripe_customer_id': fields.String(required=False),
    'created_at': fields.DateTime(required=True),
    'role': fields.String(required=True),
})

user_admin_model = user_ns.model('UserAdmin', {
    'id': fields.Integer(required=True),
    'full_name': fields.String(required=True),
    'email': fields.String(required=True),
    'role': fields.String(required=True),
})

@user_ns.route('/signup', methods=['POST'])
class SignupResource(Resource):
    @handle_exceptions
    def post(self): # Create a new user account
        data = request.get_json()

        response = UserService.create_user(data)

        return marshal(response, user_model), 201

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
    
@user_ns.route('/verify-email/<string:token>', methods=['POST'])
class VerifyEmailResource(Resource):
    @handle_exceptions
    def post(self, token):
        UserService.verify_email(token)

        return {'message': 'Email verified successfully'}, 200
    
@user_ns.route('/resend-verification', methods=['POST'])
class ResendVerificationResource(Resource):
    @handle_exceptions
    def post(self):
        data = request.get_json()

        UserService.resend_verification_email(data)

        return {'message': 'Verification email sent successfully'}, 200

@user_ns.route('/logout', methods=['POST'])
class LogoutResource(Resource):
    # @jwt_required()
    @handle_exceptions
    def post(self):
        response = jsonify({'message': 'Logout successful'})
        unset_jwt_cookies(response) # Unset the jwt cookies, effectively logging the user out
        return response
    
@user_ns.route('/reset-password', methods=['POST'])
class ResetPasswordResource(Resource):
    @handle_exceptions
    def post(self): # Send a password reset email
        data = request.get_json()

        UserService.send_password_reset_email(data)

        return {'message': 'Password reset email sent successfully'}, 200
    
@user_ns.route('/reset-password/<string:token>', methods=['PUT'])
class ResetPasswordResource(Resource):
    @handle_exceptions
    def put(self, token): # Reset the user password
        data = request.get_json()
        
        UserService.reset_password(token, data)    
        
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
    
@user_ns.route('/contact-us', methods=['POST'])
class ContactUsResource(Resource):
    @handle_exceptions    
    @limiter.limit("2 per day") # Limit the number of requests to 2 per day
    def post(self): # Send contact us email
        data = request.get_json()

        UserService.send_contact_us_email(data)

        return {'message': 'Email sent successfully, thanks for getting in touch!'}, 200

@user_ns.route('/admin', methods=['GET', 'DELETE'])
class AdminResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self): # Get all users
        page = request.args.get('page', 1, type=int)

        results = UserService.get_all_admin_users(page)

        response = {
            'users': marshal(results['users'], user_admin_model),
            'total_pages': results['total_pages'],
            'current_page': results['current_page'],
            'total_users': results['total_users']
        }

        return response, 200
    
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def delete(self): # Delete all old guest users
        UserService.delete_old_guest_users()

        return {'message': 'Old guest users deleted successfully'}, 200
        
@user_ns.route('/admin/<int:user_id>', methods=['GET'])
class AdminResouce(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self, user_id): # Get a user
        user = UserService.get_user(user_id)

        return marshal(user, user_model), 200

@user_ns.route('/admin/dashboard', methods=['GET'])
class AdminResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self): # Get the dashboard data
        results = UserService.get_dashboard_data()

        response = {
            'total_users': results['total_users'],
            'ongoing_orders': results['ongoing_orders'],
            'orders_overall': results['orders_overall'],
            'total_revenue': results['total_revenue'],
            'graph_data': results['graph_data']
        }

        return response, 200