from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from models import Cart, CartProduct, Product
from main import create_app
from celery_worker import celery
import os
from config import Development, Production
import redis
from exts import cache
from services.product_service import ProductService

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

# Set redis client
redis_client = redis.StrictRedis.from_url(config.CACHE_REDIS_URL)

# Initialise app
app = create_app(config)

@celery.task(name="tasks.cart_cleanup.cleanup_abandoned_carts")
def cleanup_abandoned_carts():
    lock_key = "lock:product_reserved_stock"
    cache_needs_clearing = False

    # Try to acquire the lock
    if not redis_client.set(lock_key, "1", nx=True, ex=LOCK_EXPIRATION):
        print("cleanup_abandoned_carts task is already running.")
        return

    try:
        with app.app_context():
            now = datetime.now(tz=ZoneInfo("UTC"))
            carts = Cart.query.all()

            for cart in carts:
                # Unlock carts locked > 24h ago, meaning any cart that been locked due to abandoned stripe checkout session
                if cart.locked and cart.locked_at and (now - cart.locked_at > timedelta(hours=24)):
                    cart.locked = False
                    cart.locked_at = None
                    print(f"Unlocked cart {cart.id}")
                    cart.save()

                # Clean up stale carts
                # If the cart is not locked and the product was added more than 60 minutes ago, remove the product from the cart and release the reserved stock
                if not cart.locked and cart.product_added_at and (now - cart.product_added_at > timedelta(hours=1)):
                    for cp in cart.cart_products:
                        product = Product.query.get(cp.product_id)
                        if product:
                            product.reserved_stock = max(product.reserved_stock - cp.quantity, 0) # Ensure stock doesn't go negative
                            # product.reserved_stock -= cp.quantity
                            product.save()
                    CartProduct.query.filter_by(cart_id=cart.id).delete()
                    cart.product_added_at = None
                    print(f"Cleaned up cart {cart.id}")
                    cart.save()
                    cache_needs_clearing = True

        # Clear the cache
        if cache_needs_clearing:
            cache.delete_memoized(ProductService.get_all_products)

    finally:
        # Release the lock
        redis_client.delete(lock_key)
        print("Lock released for cleanup_abandoned_carts task.")