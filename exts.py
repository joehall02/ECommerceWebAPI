from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from config import Test
import redis

# Create an instance of SQLAlchemy, which will be used to interact with the database
db = SQLAlchemy()

# Create an instance of Limiter, which will be used to rate limit the contact us endpoint
limiter = Limiter(key_func=get_remote_address)

# Create an instance of Cache
cache = Cache()

# Create an instance of Redis
redis_client = None # Will be set in init_extensions

def init_extensions(app, config):
    global redis_client

    storage_uri = app.config['CACHE_REDIS_URL']
    
    # Set up Redis client if not in test mode
    if config != Test:
        redis_client = redis.StrictRedis.from_url(storage_uri)

    limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)
    
    # Initialise the database
    db.init_app(app)
    
    # Initialise the rate limiter
    limiter.init_app(app)

    # Initialise the cache
    cache.init_app(app)