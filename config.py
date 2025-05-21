import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv() # Load environment variables from the .env file

# Configuration class
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') # Get the secret key from the environment variables
    SECURITY_SALT = os.getenv('SECURITY_SALT') # Get the security salt from the environment variables
    FRONTEND_ORIGIN_URL = os.getenv('FRONTEND_ORIGIN_URL', 'http://localhost:3000') # Get the frontend origin URL from the environment variables
    FRONTEND_PUBLIC_URL = os.getenv('FRONTEND_PUBLIC_URL', 'http://localhost:3000') # Get the frontend public URL from the environment variables
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30) # Set the access token expiry time
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7) # Set the refresh token expiry time
    JWT_REFRESH_TOKEN_REMEMBER_ME_EXPIRES = timedelta(days=30) # Set the remember me refresh token expiry time
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token'
    JWT_COOKIE_CSRF_PROTECT = False  # Set to True to enable CSRF protection        
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY') # Get the Stripe API key from the environment variables
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET') # Get the Stripe webhook secret from the environment variables
    MAILGUN_DOMAIN_NAME = os.getenv('MAILGUN_DOMAIN_NAME') # Get the MAILGUN domain name from the environment variables
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY') # Get the MAILGUN API key from the environment variables
    MAILGUN_SENDER_EMAIL = os.getenv('MAILGUN_SENDER_EMAIL') # Get the MAILGUN sender email from the environment variables
    CONTACT_US_EMAIL = os.getenv('CONTACT_US_EMAIL') # Get the contact us email from the environment variables
    CACHE_TYPE = 'RedisCache' # Set the cache type to Redis
    GOOGLE_CLOUD_STORAGE_BUCKET_NAME = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET_NAME') # Get the Google Cloud Storage bucket name from the environment variables

# Development configuration class
class Development(Config):
    DEBUG = True # Enable debug mode
    SQLALCHEMY_DATABASE_URI = os.getenv('DEVELOPMENT_DATABASE_URI') # Get the database URL from the environment variables
    JWT_COOKIE_SECURE = True # Set to True to enable secure cookies
    JWT_COOKIE_SAMESITE = 'None' # Set the SameSite attribute for cookies
    CACHE_REDIS_URL = os.getenv('DEVELOPMENT_REDIS_URL') # Get the Redis URL from the environment variables
    CELERY_BROKER_URL = os.getenv('DEVELOPMENT_REDIS_URL') # Get the Celery broker URL from the environment variables
    CELERY_RESULT_BACKEND = os.getenv('DEVELOPMENT_REDIS_URL') # Get the Celery result backend URL from the environment variables

# Production configuration class
class Production(Config):    
    JWT_COOKIE_SECURE = True # Set to True to enable secure cookies
    JWT_COOKIE_SAMESITE = 'Lax' # Set the SameSite attribute for cookies
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCTION_DATABASE_URI') # Get the database URL from the environment variables
    CACHE_REDIS_URL = os.getenv('PRODUCTION_REDIS_URL') # Get the Redis URL from the environment variables
    CELERY_BROKER_URL = os.getenv('PRODUCTION_REDIS_URL') # Get the Celery broker URL from the environment variables
    CELERY_RESULT_BACKEND = os.getenv('PRODUCTION_REDIS_URL') # Get the Celery result backend URL from the environment variables

# Test configuration class
class Test(Config):
    TESTING = True # Enable testing mode
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI') # Get the test database URL from the environment variables    
    JWT_COOKIE_SECURE = False # Allow cookies to be sent over http in testing
    JWT_COOKIE_SAMESITE = None # Set the SameSite attribute for cookies to None in testing
    CACHE_TYPE = 'SimpleCache' # Set the cache type to SimpleCache for testing
    CACHE_DEFAULT_TIMEOUT = 300 # Set the cache timeout to 5 minutes, this makes sure that the cache is cleared after 5 minutes
    CACHE_REDIS_URL = "memory://" # Use in-memory Redis for testing