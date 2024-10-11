from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import User
from flask import current_app, request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from schemas import SignupSchema, LoginSchema
from services.user_service import UserService

# Define the schema instances
signup_schema = SignupSchema()
login_schema = LoginSchema()        

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