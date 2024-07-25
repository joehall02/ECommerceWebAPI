from datetime import timedelta
from flask import Flask
from flask_restx import Api
from config import Development, Test
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv
from exts import db
import os
from models import User, Address, Payment, Category, Product, Cart, Order, OrderItem, CartProduct, ProductImage, FeaturedProduct
from api.user import user_ns
from api.category import category_ns
from api.product import product_ns
from api.order import order_ns
from api.payment import payment_ns
from api.address import address_ns
from api.cart import cart_ns

def create_app(config=Development):
    # Create an instance of the Flask app
    app = Flask(__name__)

    # Set the app configuration
    app.config.from_object(config)

    # Initialize the database
    db.init_app(app)

    # Initialize the JWT manager
    jwt = JWTManager(app)

    # Initialize the migration engine
    migrate = Migrate(app, db)

    # Create an instance of the API
    api = Api(app, doc='/docs') 

    # # If the configuration is Test, upgrade the database to the latest migration
    if config == Test:
        with app.app_context():
            db.create_all()
            upgrade()

    # Import the namespaces
    api.add_namespace(user_ns)
    api.add_namespace(category_ns)
    api.add_namespace(product_ns)
    api.add_namespace(order_ns)
    api.add_namespace(payment_ns)
    api.add_namespace(address_ns)
    api.add_namespace(cart_ns)

    return app