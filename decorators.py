from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from models import User
from werkzeug.exceptions import TooManyRequests


def admin_required():
    def decorator(fn):
        @wraps(fn)        
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if user.role != 'admin':
                return {'error': 'Unauthorized access'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def customer_required():
    def decorator(fn):
        @wraps(fn)        
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if user.role != 'customer' and user.role != 'admin':
                return {'error': 'Unauthorized access'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except TooManyRequests as e:
            return {'error': 'Reached limit for today. Please try again later.'}, 429
        except Exception as e:
            print('ERROR:', e)
            return {'error': str(e)}, 500
            # return {'error': 'An unexpected error occured. Please try again later.'}, 500
        
    return decorator