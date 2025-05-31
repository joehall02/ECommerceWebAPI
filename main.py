from flask import Flask, request
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from exts import db, init_extensions, limiter, cache
from api.user import user_ns
from api.category import category_ns
from api.product import product_ns
from api.order import order_ns
from api.address import address_ns
from api.cart import cart_ns
import stripe
from jwt import ExpiredSignatureError
from flask_jwt_extended.exceptions import NoAuthorizationError
import os

def create_app(config):
    # Create an instance of the Flask app
    app = Flask(__name__)

    # Set the app configuration
    app.config.from_object(config)

    # Initialise the extensions, db, limiter, cache and redis
    init_extensions(app, config)

    # Initialise the Stripe API
    stripe.api_key = app.config.get('STRIPE_API_KEY')

    # Initialise the Stripe webhook secret
    stripe.webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')

    # Enable CORS
    CORS(app, resources={
    r"/*": {
            "origins": app.config.get('FRONTEND_ORIGIN_URL'),
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization", "X-Frontend-Secret"]
        }
    })
    
    # Initialise the JWT manager
    jwt = JWTManager(app)

    # Initialise the migration engine
    migrate = Migrate(app, db)

    # Create an instance of the API
    api = Api(app, doc=False) 

    # Import the namespaces
    api.add_namespace(user_ns)
    api.add_namespace(category_ns)
    api.add_namespace(product_ns)
    api.add_namespace(order_ns)
    api.add_namespace(address_ns)
    api.add_namespace(cart_ns)

    # Restrict api access to the frontend
    @app.before_request
    def restrict_api_access():
        if os.getenv('FLASK_ENV') == 'production':
            # Skip the check for stripe webhook endpoint
            if request.path == '/order/webhook':
                return
            
            expected_secret = app.config.get("FRONTEND_SECRET_HEADER")
            secret_header = request.headers.get('X-Frontend-Secret')

            # If the secret header is not present or does not match the expected secret, return a 403 error
            if secret_header != expected_secret:
                return {'error': 'Forbidden'}, 403

    # Error handler for 401 error when user is logged out
    @api.errorhandler(NoAuthorizationError)
    def handle_no_authorisation_error(e):
        return {'error': 'Missing or invalid token'}, 401
    
    @api.errorhandler(ExpiredSignatureError)
    def handle_expired_signature_error(e):
        return {'error': 'Missing or invalid token'}, 401

    return app