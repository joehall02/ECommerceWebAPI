from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from models import User, Cart, Product
from celery_worker import celery, flask_app, redis_client
import os
from exts import cache
from services.user_service import UserService
from services.product_service import FeaturedProductService, ProductService

# Lock expiration
LOCK_EXPIRATION = 60 * 30  # 30 minutes

# Determine the environment
delete_guest_users_days = int(os.getenv('DELETE_GUEST_USERS_DAYS', 7))  # Default to 7 days

@celery.task(name="tasks.guest_cleanup.cleanup_old_guest_users")
def cleanup_old_guest_users():
    with flask_app.app_context():    
        lock_key = "lock:product_reserved_stock"
        cache_needs_clearing = False

        # Try to acquire the lock
        if not redis_client.set(lock_key, "1", nx=True, ex=LOCK_EXPIRATION):
            print("cleanup_old_guest_users task is already running.")
            return
        
        try:
            now = datetime.now(tz=ZoneInfo("UTC"))
            guests = User.query.filter_by(role='guest').all()

            for guest in guests:
                # Check if the user was created more than delete guest user days ago
                if now - guest.created_at > timedelta(days=delete_guest_users_days):
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
                    cache_needs_clearing = True
            
            # Clear the cache
            if cache_needs_clearing:
                cache.delete_memoized(UserService.get_all_admin_users)
                cache.delete_memoized(UserService.get_dashboard_data)           
                # cache.delete_memoized(ProductService.get_all_products)
                # cache.delete_memoized(FeaturedProductService.get_all_featured_products)


        finally:
            # Release the lock
            redis_client.delete(lock_key)
            print("Lock released for cleanup_old_guest_users task.")