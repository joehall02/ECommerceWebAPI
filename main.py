from flask import Flask
from flask_restx import Api
from config import Development, Test
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
from flask_cors import CORS
from exts import db, init_extensions, limiter, cache
from api.user import user_ns
from api.category import category_ns
from api.product import product_ns
from api.order import order_ns
from api.address import address_ns
from api.cart import cart_ns
import stripe
from apscheduler.schedulers.background import BackgroundScheduler
from services.user_service import UserService

def create_app(config=Development):
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
    # api = Api(app, doc='/docs') 
    api = Api(app) 

    # # If the configuration is Test, upgrade the database to the latest migration
    # if config == Test:
    #     with app.app_context():
    #         db.create_all()
    #         upgrade()

    # Import the namespaces
    api.add_namespace(user_ns)
    api.add_namespace(category_ns)
    api.add_namespace(product_ns)
    api.add_namespace(order_ns)
    api.add_namespace(address_ns)
    api.add_namespace(cart_ns)

    # Start backgrounud jobs
    def start_scheduler(app=app):
        print('Starting scheduler')
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: UserService.delete_old_guest_users(app), 'interval', hours=1) # Delete guest users
        scheduler.start()

    # Start the scheduler
    start_scheduler()

    return app