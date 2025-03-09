from flask import jsonify, make_response, current_app
from marshmallow import ValidationError
from models import Cart, CartProduct, Product
from flask_jwt_extended import get_jwt_identity, set_access_cookies, set_refresh_cookies
from schemas import CartSchema, CartProductSchema, ProductSchema, ProductCartProductCombinedSchema
from services.user_service import UserService

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
        
        cart_products = cart.cart_products

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
        
        # Update the cart product quantity
        cart_product.quantity = valid_data['quantity']

        cart_product.save()

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
            existing_cart_product.quantity = valid_data['quantity']
            existing_cart_product.save()
            return existing_cart_product

        # Otherwise create a new cart product if it doesn't exist already
        cart_product = CartProduct(
            quantity = valid_data['quantity'],
            product_id = product_id,
            cart_id = cart.id
        )

        cart_product.save()

        # Serialise the cart product
        cart_product_data = cart_product_schema.dump(cart_product)

        # Create a response
        response = make_response(jsonify(cart_product_data))

        # If a guest user was created, set the user token to the response
        if 'guest_response' in locals():
            # response.headers['x-access-csrf-token'] = guest_response.headers['x-access-csrf-token']
            # response.headers['x-refresh-csrf-token'] = guest_response.headers['x-refresh-csrf-token']
            set_access_cookies(response, guest_response.json['access_token'])
            set_refresh_cookies(response, guest_response.json['refresh_token'])

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
        
        # If the cart product has a quantity of 1, delete the cart product
        cart_product.delete()

        return cart_product