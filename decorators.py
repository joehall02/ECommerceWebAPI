from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User


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