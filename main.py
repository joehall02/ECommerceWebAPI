from datetime import timedelta
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from exts import db
import os
from models import User, Address, Payment, Category, Product, Cart, Order, OrderItem, CartProduct, ProductImage, FeaturedProduct
from api.auth import auth_ns
from api.administrator import admin_ns

load_dotenv() # Load environment variables from .env file

def create_app():
    DATABASE_URL = os.getenv('DATABASE_URL') # Get the database URL from the environment variables
    SECRET_KEY = os.getenv('SECRET_KEY') # Get the secret key from the environment variables
    
    # Create an instance of the Flask app
    app = Flask(__name__)

    # Enable debug mode
    app.debug = True

    # Set the database URL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL # Set the database URL
    app.config['SECRET_KEY'] = SECRET_KEY # Set the secret key for the app
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) # Set the access token expiry time to 1 hour

    # Initialize the database
    db.init_app(app)

    # Initialize the JWT manager
    jwt = JWTManager(app)

    # Create an instance of the API
    api = Api(app, doc='/docs') 

    # Import the namespaces
    api.add_namespace(auth_ns)
    api.add_namespace(admin_ns)

    return app