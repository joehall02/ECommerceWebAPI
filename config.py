import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv() # Load environment variables from the .env file

# Configuration class
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') # Get the secret key from the environment variables
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # Set the access token expiry time to 1 hour

# Development configuration class
class Development(Config):
    DEBUG = True # Enable debug mode
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') # Get the database URL from the environment variables

# Production configuration class
class Production(Config):
    pass

# Test configuration class
class Test(Config):
    TESTING = True # Enable testing mode
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI') # Get the test database URL from the environment variables