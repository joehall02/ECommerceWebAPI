from marshmallow import ValidationError
from models import Cart, CartProduct, Product
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import get_jwt_identity, jwt_required
from schemas import CartSchema, CartProductSchema, ProductSchema, ProductCartProductCombinedSchema
from services.cart_service import CartService

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

        products = []

        # get the products and add it to an array using each item's product_id in cart_products
        for cart_product in cart_products:
            product = Product.query.get(cart_product.product_id)
            products.append({
                'cart_product': cart_product,
                'product': product
            })

        return products
    
    @staticmethod
    def add_product_to_cart(product_id):
        user = get_jwt_identity()

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
        
        # Check if the cart product already exists, if it does, increment the quantity by 1
        existing_cart_product = CartProduct.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if existing_cart_product:
            existing_cart_product.quantity += 1
            existing_cart_product.save()
            return existing_cart_product

        # Create a new cart product if it doesn't exist already
        cart_product = CartProduct(
            quantity = 1, # Starts with a quantity of 1 since the product is being added for the first time
            product_id = product_id,
            cart_id = cart.id
        )

        cart_product.save()

        return cart_product
    
    @staticmethod
    def delete_product_from_cart(cart_product_id):
        cart_product = CartProduct.query.get(cart_product_id)

        # Check if the cart product exists
        if not cart_product:
            raise ValidationError('Cart product not found')
        
        # If the cart product has a quantity greater than 1, decrement the quantity by 1
        if cart_product.quantity > 1:
            cart_product.quantity -= 1
            cart_product.save()
            return cart_product
        
        # If the cart product has a quantity of 1, delete the cart product
        cart_product.delete()

        return cart_product
        

cart_ns = Namespace('cart', description='Cart operations')

# Define the models used for api documentation,
# actual validation is done using the schema
cart_model = cart_ns.model('Cart', {
    'user_id': fields.Integer(required=True),
})

cart_product_model = cart_ns.model('CartProduct', {
    'quantity': fields.Integer(required=True),
    'product_id': fields.Integer(required=True),
    'cart_id': fields.Integer(required=True),
})  

product_model = cart_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True),
    'category_id': fields.Integer(required=True),
})

combined_model = cart_ns.model('Combined', {
    'cart_product': fields.Nested(cart_product_model),
    'product': fields.Nested(product_model),
})

# Define the routes for cart operations
@cart_ns.route('/', methods=['GET'])
class CartProductResource(Resource):
    @jwt_required()
    def get(self):
        try:
            products = CartService.get_all_products_in_cart()
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        try:
            products = product_cart_product_combined_schema.dump(products, many=True)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return marshal(products, combined_model), 200

@cart_ns.route('/<int:cart_product_id>', methods=['DELETE'])
class CartProductDetailResource(Resource):
    @jwt_required()
    def delete(self, cart_product_id):
        try:
            CartService.delete_product_from_cart(cart_product_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Product deleted from cart successfully'}, 200
    
@cart_ns.route('/<int:product_id>', methods=['POST'])
class CartProductAddResource(Resource):
    @jwt_required()
    def post(self, product_id):
        # Add the product to the cart
        try:
            CartService.add_product_to_cart(product_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Product added to cart successfully'}, 201