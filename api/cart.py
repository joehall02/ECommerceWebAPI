from marshmallow import ValidationError
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from services.cart_service import CartService
        
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
    def get(self): # Get all products in the cart
        try:
            products = CartService.get_all_products_in_cart()
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return marshal(products, combined_model), 200

@cart_ns.route('/<int:cart_product_id>', methods=['DELETE'])
class CartProductDetailResource(Resource):
    @jwt_required()
    def delete(self, cart_product_id): # Delete a product from the cart
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
    def post(self, product_id): # Add a product to the cart        
        try:
            CartService.add_product_to_cart(product_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Product added to cart successfully'}, 201