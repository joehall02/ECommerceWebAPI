from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import redis
import os

# Create an instance of SQLAlchemy, which will be used to interact with the database
db = SQLAlchemy()

# Create an instance of Limiter, which will be used to rate limit the contact us endpoint
limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv('REDIS_URL'))

# Create an instance of Redis
redis_client = redis.StrictRedis.from_url(os.getenv('REDIS_URL'))

# Create an instance of Cache
cache = Cache()