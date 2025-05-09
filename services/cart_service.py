from datetime import datetime
from flask import jsonify, make_response
from marshmallow import ValidationError
from models import Cart, CartProduct, Product
from flask_jwt_extended import get_jwt_identity, set_access_cookies, set_refresh_cookies
from schemas import CartSchema, CartProductSchema, ProductSchema, ProductCartProductCombinedSchema
from services.product_service import ProductService
from services.user_service import UserService
from exts import cache

# Define the schema instances
cart_schema = CartSchema()
cart_product_schema = CartProductSchema()
product_schema = ProductSchema()
product_cart_product_combined_schema = ProductCartProductCombinedSchema()

# Services
class CartService:
    @staticmethod
    def get_all_products_in_cart():
        user = get_jwt_identity()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        cart = Cart.query.filter_by(user_id=user).first()

        # Check if the cart exists
        if not cart:
            raise ValidationError('Cart not found')
        
        # cart_products = cart.cart_products
        cart_products = CartProduct.query.filter_by(cart_id=cart.id).order_by(CartProduct.id.desc()).all()

        cart_products_and_products = []

        # get the products and add it to an array using each item's product_id in cart_products
        for cart_product in cart_products:
            product = Product.query.get(cart_product.product_id)
            image_path = product.product_images[0].image_path if product.product_images else None # Get the first image path if it exists, otherwise set it to None
            cart_products_and_products.append({
                'cart_product': cart_product,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock,
                    'image_path': image_path,
                    'category_name': product.category.name
                }
            })

        # Serialize the products array
        products = product_cart_product_combined_schema.dump(cart_products_and_products, many=True)

        return products
    
    @staticmethod
    def update_product_quantity_in_cart(data, cart_product_id):
        # Check if the cart product id is provided
        if not cart_product_id:
            raise ValidationError('No cart product id provided')
        
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')
        
        # Validate the request data against the cart product schema
        valid_data = cart_product_schema.load(data, partial=True) # partial=True allows for partial data to be validated

        cart_product = CartProduct.query.get(cart_product_id)

        # Check if the cart product exists
        if not cart_product:
            raise ValidationError('Cart product not found')

        # Reserve the stock for the product
        product = Product.query.get(cart_product.product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')

        # if product.stock < valid_data['quantity'] or product.reserved_stock < valid_data['quantity']:
        #     raise ValidationError('Product is out of stock')
        
        # Calculate the difference in quantity
        quantity_difference = valid_data['quantity'] - cart_product.quantity

        if product.stock < quantity_difference + product.reserved_stock:
            raise ValidationError('Product is out of stock.')
        
        # Reserve the stock for the product
        product.reserved_stock += quantity_difference
        product.save()

        # Update the cart product quantity
        cart_product.quantity = valid_data['quantity']
        cart_product.save()

        # Clear the cache
        cache.delete_memoized(ProductService.get_all_products)

        return cart_product

    @staticmethod
    def add_product_to_cart(data, product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')
        
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the cart product schema
        valid_data = cart_product_schema.load(data, partial=True) # partial=True allows for partial data to be validated

        # Get the user if JWT is provided, else create a guest user        
        user = get_jwt_identity()
        
        # Create guest user if user is not found
        if not user:
            user, guest_response = UserService.create_guest_user()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        cart = Cart.query.get(user)

        # Check if the cart exists
        if not cart:
            raise ValidationError('Cart not found')
        
        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        # Check if the product is in stock
        if product.stock < valid_data['quantity']:
            raise ValidationError('Product is out of stock')

        # If the cart product already exists, change the quantity to the new quantity
        existing_cart_product = CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if existing_cart_product:
            # Calculate the difference in quantity
            quantity_difference = valid_data['quantity'] - existing_cart_product.quantity

            # Adjust the reserved stock
            if product.stock < quantity_difference + product.reserved_stock:
                raise ValidationError('Product is out of stock.')
            
            # Reserve the stock for the product
            product.reserved_stock += quantity_difference
            product.save()

            # Update the cart product quantity
            existing_cart_product.quantity = valid_data['quantity']
            existing_cart_product.save()
            return cart_product_schema.dump(existing_cart_product)

        # Reserve the stock for the product
        if product.stock < valid_data['quantity'] + product.reserved_stock:
            raise ValidationError('Product is out of stock.')
        
        product.reserved_stock += valid_data['quantity']
        product.save()

        # Otherwise create a new cart product if it doesn't exist already
        cart_product = CartProduct(
            quantity = valid_data['quantity'],
            product_id = product_id,
            cart_id = cart.id
        )

        cart_product.save()

        # Serialise the cart product
        cart_product_data = cart_product_schema.dump(cart_product)

        # Add timestamp of when cart product was added
        cart.product_added_at = datetime.now()
        cart.save()

        # Create a response
        response = make_response(jsonify(cart_product_data))

        # If a guest user was created, set the user token to the response
        if 'guest_response' in locals():  
            set_access_cookies(response, guest_response.json['access_token'])
            set_refresh_cookies(response, guest_response.json['refresh_token'])

            print(guest_response.json['access_token'])
            print(guest_response.json['refresh_token'])

        # Clear the cache
        cache.delete_memoized(ProductService.get_all_products)

        return response
    
    @staticmethod
    def delete_product_from_cart(cart_product_id):
        # Check if the cart product id is provided
        if not cart_product_id:
            raise ValidationError('No cart product id provided')

        cart_product = CartProduct.query.get(cart_product_id)

        # Check if the cart product exists
        if not cart_product:
            raise ValidationError('Cart product not found')
        
        # Restore the stock for the product
        product = Product.query.get(cart_product.product_id)
        if product:
            # product.reserved_stock -= cart_product.quantity
            product.reserved_stock = max(product.reserved_stock - cart_product.quantity, 0) # Ensure stock doesn't go negative
            product.save()
        
        # If the cart product has a quantity of 1, delete the cart product
        cart_product.delete()

        # Clear the cache
        cache.delete_memoized(ProductService.get_all_products)

        return cart_product