import os
from datetime import timedelta
from dotenv import load_dotenv
import stripe

load_dotenv() # Load environment variables from the .env file

# Configuration class
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') # Get the secret key from the environment variables
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') # Get the JWT secret key from the environment variables
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30) # Set the access token expiry time
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7) # Set the refresh token expiry time
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token'
    JWT_COOKIE_CSRF_PROTECT = True  # Set to True to enable CSRF protection    
    JWT_COOKIE_SECURE = True # Set to True to enable secure cookies
    JWT_COOKIE_SAMESITE = 'None' # Set the SameSite attribute for cookies    
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY') # Get the Stripe API key from the environment variables
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET') # Get the Stripe webhook secret from the environment variables

# Development configuration class
class Development(Config):
    DEBUG = True # Enable debug mode
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') # Get the database URL from the environment variables

# Production configuration class
class Production(Config):
    JWT_COOKIE_SECURE = True
    pass

# Test configuration class
class Test(Config):
    TESTING = True # Enable testing mode
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI') # Get the test database URL from the environment variables