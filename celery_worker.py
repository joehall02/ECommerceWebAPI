import ssl
import os
from celery import Celery
from config import Development, Production
from celery.schedules import crontab

# Determine is ssl certification is required based on the environment
# ssl certification required for celery when using upstash
flask_env = os.getenv('FLASK_ENV', 'development')
redis_ssl_required = os.getenv('REDIS_SSL_REQUIRED', 'False')

# Set up configuration based on the environment
if flask_env == 'development':
    config = Development
elif flask_env == 'production':
    config = Production
else:
    raise ValueError(f"Invalid FLASK_ENV value: {flask_env}. Expected 'development' or 'production'.")

celery = Celery(
    __name__,
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=['tasks.cart_cleanup', 'tasks.guest_cleanup'],  # Load tasks from this module
)

# Configure Celery
celery_conf = {
    'timezone': 'UTC',
    'enable_utc': True,
    'beat_scheduler': 'redbeat.RedBeatScheduler', # Use Redbeat for periodic tasks
    'redbeat_redis_url': config.CELERY_BROKER_URL, # Point Redbeat to Redis
    'beat_schedule': {
        'cleanup-abandoned-carts-every-10-mins': {
            'task': 'tasks.cart_cleanup.cleanup_abandoned_carts',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
        },
        'cleanup-old-guest-users-every-15-mins': {
            'task': 'tasks.guest_cleanup.cleanup_old_guest_users',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
        },
    }
}

# Set up Redis SSL if required
if redis_ssl_required == 'True':
    celery_conf['broker_use_ssl'] = {'ssl_cert_reqs': ssl.CERT_REQUIRED}
    celery_conf['redis_backend_use_ssl'] = {'ssl_cert_reqs': ssl.CERT_REQUIRED}

celery.conf.update(celery_conf)