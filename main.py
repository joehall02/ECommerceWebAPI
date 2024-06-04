from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
from exts import db
import os
from models import User, Address, Payment, Category, Product, Cart, Order, OrderItem, CartProduct, ProductImage, FeaturedProduct
from api.auth import auth_ns


def create_app():
    load_dotenv() # Load environment variables from .env file
    DATABASE_URL = os.getenv('DATABASE_URL') # Get the database URL from the environment variables
    
    # Create an instance of the Flask app
    app = Flask(__name__)

    # Set the database URL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL # Set the database URL

    # Initialize the database
    db.init_app(app)

    # Create an instance of the API
    api = Api(app, doc='/docs') 

    # Import the namespaces
    api.add_namespace(auth_ns)

    return app