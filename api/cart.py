from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from services.cart_service import CartService
from decorators import handle_exceptions
        
cart_ns = Namespace('cart', description='Cart operations')

# Define the models used for api documentation,
# actual validation is done using the schema
cart_model = cart_ns.model('Cart', {
    'user_id': fields.Integer(required=True),
})

cart_product_model = cart_ns.model('CartProduct', {
    'id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True),
    'product_id': fields.Integer(required=True),
    'cart_id': fields.Integer(required=True),
})  

product_model = cart_ns.model('Product', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'image_path': fields.String(required=True),
    'category_name': fields.String(required=True),
})

combined_model = cart_ns.model('Combined', {
    'cart_product': fields.Nested(cart_product_model),
    'product': fields.Nested(product_model),
})

# Define the routes for cart operations
@cart_ns.route('/', methods=['GET'])
class CartProductResource(Resource):
    @jwt_required()
    @handle_exceptions
    def get(self): # Get all products in the cart        
        products = CartService.get_all_products_in_cart()        
        
        return marshal(products, combined_model), 200

@cart_ns.route('/<int:cart_product_id>', methods=['DELETE', 'PUT'])
class CartProductDetailResource(Resource):   
    @jwt_required()
    @handle_exceptions
    def put(self, cart_product_id): # Update the quantity of a product in the cart
        data = request.get_json()

        CartService.update_product_quantity_in_cart(data, cart_product_id)

        return {'message': 'Product quantity updated successfully'}, 200

    @jwt_required()
    @handle_exceptions
    def delete(self, cart_product_id): # Delete a product from the cart        
        CartService.delete_product_from_cart(cart_product_id)        
        
        return {'message': 'Product deleted from cart successfully'}, 200
    
@cart_ns.route('/<int:product_id>', methods=['POST'])
class CartProductAddResource(Resource):
    @jwt_required()
    @handle_exceptions
    def post(self, product_id): # Add a product to the cart        
        data = request.get_json()

        CartService.add_product_to_cart(data, product_id)        
        
        return {'message': 'Product added to cart successfully'}, 201