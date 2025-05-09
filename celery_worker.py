from celery import Celery
from config import Config
from celery.schedules import crontab

celery = Celery(
    __name__,
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['tasks.cart_cleanup', 'tasks.guest_cleanup'],  # Load tasks from this module
)

celery.conf.update(
    timezone='UTC',
    enable_utc=True,
    beat_scheduler='redbeat.RedBeatScheduler', # Use Redbeat for periodic tasks
    redbeat_redis_url=Config.CELERY_BROKER_URL, # Point Redbeat to Redis
    beat_schedule={
        'cleanup-abandoned-carts-every-10-mins': {
            'task': 'tasks.cart_cleanup.cleanup_abandoned_carts',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
        },
        'cleanup-old-guest-users-every-15-mins': {
            'task': 'tasks.guest_cleanup.cleanup_old_guest_users',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
        },
    }
)
