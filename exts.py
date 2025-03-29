from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from config import Test
import redis
import os

# Create an instance of SQLAlchemy, which will be used to interact with the database
db = SQLAlchemy()

# Create an instance of Limiter, which will be used to rate limit the contact us endpoint
limiter = Limiter(key_func=get_remote_address)
# limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv('REDIS_URL'))

# Create an instance of Cache
cache = Cache()

# Create an instance of Redis
redis_client = None # Will be set in init_extensions

def init_extensions(app, config):
    global redis_client

    if config == Test:
        # Use in-memory limiter during tests
        storage_uri = "memory://"
    else:
        storage_uri = os.getenv('REDIS_URL')
        redis_client = redis.StrictRedis.from_url(os.getenv('REDIS_URL'))

    limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)
    
    # Initialise the database
    db.init_app(app)
    
    # Initialise the rate limiter
    limiter.init_app(app)

    # Initialise the cache
    cache.init_app(app)