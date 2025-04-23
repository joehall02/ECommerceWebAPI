from flask import Flask
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


def create_app(config):
    # Create an instance of the Flask app
    app = Flask(__name__)

    # Set the app configuration
    app.config.from_object(config)

    # Initialise the extensions, db, limiter, cache and redis
    init_extensions(app, config)

    # Initialise the Stripe API
    stripe.api_key = app.config['STRIPE_API_KEY']

    # Initialise the Stripe webhook secret
    stripe.webhook_secret = app.config['STRIPE_WEBHOOK_SECRET']

    # Enable CORS
    CORS(app, supports_credentials=True, origins=[app.config['FRONTEND_URL']]) 

    # Initialise the JWT manager
    jwt = JWTManager(app)

    # Initialise the migration engine
    migrate = Migrate(app, db)

    # Create an instance of the API
    api = Api(app) 

    # Import the namespaces
    api.add_namespace(user_ns)
    api.add_namespace(category_ns)
    api.add_namespace(product_ns)
    api.add_namespace(order_ns)
    api.add_namespace(address_ns)
    api.add_namespace(cart_ns)

    # Error handler for 401 error when user is logged out
    @api.errorhandler(NoAuthorizationError)
    def handle_no_authorisation_error(e):
        return {'error': 'Missing or invalid token'}, 401
    
    @api.errorhandler(ExpiredSignatureError)
    def handle_expired_signature_error(e):
        return {'error': 'Missing or invalid token'}, 401

    return app