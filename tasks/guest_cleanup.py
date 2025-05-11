from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from models import User, Cart, Product
from main import create_app
from celery_worker import celery
import os
from config import Development, Production
import redis
from exts import cache
from services.user_service import UserService
from services.product_service import ProductService

# Redis setup for locking
redis_client = redis.StrictRedis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Lock expiration
LOCK_EXPIRATION = 60 * 30  # 30 minutes

# Determine the environment
flask_env = os.getenv('FLASK_ENV', 'development')

# Set the configuration based on the environment
if flask_env == 'development':
    config = Development
elif flask_env == 'production':
    config = Production
else:
    raise ValueError(f"Invalid FLASK_ENV value: {flask_env}. Expected 'development' or 'production'.")


app = create_app(config)

@celery.task(name="tasks.guest_cleanup.cleanup_old_guest_users")
def cleanup_old_guest_users():
    lock_key = "lock:product_reserved_stock"

    # Try to acquire the lock
    if not redis_client.set(lock_key, "1", nx=True, ex=LOCK_EXPIRATION):
        print("cleanup_old_guest_users task is already running.")
        return
    
    try:
        with app.app_context():
            now = datetime.now(tz=ZoneInfo("UTC"))
            guests = User.query.filter_by(role='guest').all()

            for guest in guests:
                # Check if the user was created more than 7 days ago
                if now - guest.created_at > timedelta(days=7):
                    # Clean up stale carts
                    cart = Cart.query.filter_by(user_id=guest.id).first()

                    if cart:                        
                    # For each cart product, release the reserved stock
                        for cp in cart.cart_products:
                            product = Product.query.get(cp.product_id)
                            if product:
                                product.reserved_stock = max(product.reserved_stock - cp.quantity, 0)
                                product.save()                        
                    # Delete the guest user, also deleting the cart and cart products
                    guest.delete()
                    print(f"Deleted guest user {guest.id}")
            
            # Clear the cache
            cache.delete_memoized(UserService.get_all_admin_users)
            cache.delete_memoized(UserService.get_dashboard_data)           
            cache.delete_memoized(ProductService.get_all_products)

    finally:
        # Release the lock
        redis_client.delete(lock_key)
        print("Lock released for cleanup_old_guest_users task.")

