from marshmallow import ValidationError
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from schemas import ProductSchema, ProductImageSchema, FeaturedProductSchema
from decorators import admin_required
from services.product_service import ProductService, FeaturedProductService, ProductImageService

# Define the schema instances
product_schema = ProductSchema()
featured_product_schema = FeaturedProductSchema()
product_image_schema = ProductImageSchema()

# Define the namespace for the product routes
product_ns = Namespace('product', description='Product operations')

# Define the models used for api documentation,
# actual validation is done using the schema
product_model = product_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True),
    'category_id': fields.Integer(required=True),
})

featured_product_model = product_ns.model('FeaturedProduct', {
    'product_id': fields.Integer(required=True),
})

product_image_model = product_ns.model('ProductImage', {
    'image_path': fields.String(required=True),
    'product_id': fields.Integer(required=True),
})

# Define the routes for the product operations
@product_ns.route('/', methods=['GET'])
class ProductResource(Resource):
    @jwt_required()
    def get(self): # Get all products
        try:
            products = ProductService.get_all_products()
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        try:
            products = product_schema.dump(products, many=True) # Serialize the products
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(products, product_model), 200
        
@product_ns.route('/<int:product_id>', methods=['GET'])
class ProductResource(Resource):
    @jwt_required()
    def get(self, product_id): # Get a single product
        # Get the product
        try:
            product = ProductService.get_product(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Serialize the product
        try:
            product = product_schema.dump(product) # Serialize the product
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(product, product_model), 200
    
# Define Featured Product routes for featured product operations
@product_ns.route('/featured-product', methods=['GET'])
class FeaturedProductResource(Resource):
    @jwt_required()
    def get(self): # Get all featured products        
        try:
            featured_products = FeaturedProductService.get_all_featured_products()
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Serialise the featured products
        try:
            featured_products = product_schema.dump(featured_products, many=True) # Serialize the featured products using the product schema
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(featured_products, product_model), 200 # return product_model

@product_ns.route('/featured-product/<int:featured_product_id>', methods=['GET'])
class FeaturedProductResource(Resource):
    @jwt_required()
    def get(self, featured_product_id): # Get a single featured product
        try:
            featured_product = FeaturedProductService.get_featured_product(featured_product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Serialize the featured product
        try:
            featured_product = product_schema.dump(featured_product) # Serialize the featured product using the product schema
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(featured_product, product_model), 200 # return product_model

@product_ns.route('/product-image/<int:product_id>', methods=['GET'])
class ProductImageResource(Resource):
    @jwt_required()
    def get(self, product_id): # Get all product images for a product
        try:
            product_images = ProductImageService.get_all_product_images(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        try:
            product_images = product_image_schema.dump(product_images, many=True) # Serialize the product images
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(product_images, product_image_model), 200

@product_ns.route('/admin', methods=['POST'])
class AdminProductResource(Resource):
    @jwt_required()
    @admin_required()
    def post(self): # Create a new product
        data = request.get_json()

        # Validate the request data
        try:
            valid_data = product_schema.load(data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Create a new product
        try:
            ProductService.create_product(valid_data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product created successfully'}, 201

@product_ns.route('/admin/<int:product_id>', methods=['PUT', 'DELETE'])
class AdminProductResource(Resource):
    @jwt_required()
    @admin_required()
    def put(self, product_id): # Edit a product
        data = request.get_json()

        # Validate the request data
        try:
            valid_data = product_schema.load(data, partial=True) # Allow partial product schema
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Update the product
        try:
            ProductService.update_product(valid_data, product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product updated successfully'}, 200
        
    @jwt_required()
    @admin_required()
    def delete(self, product_id): # Delete a product
        # Delete the product
        try:
            ProductService.delete_product(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product deleted successfully'}, 200
    
@product_ns.route('/admin/featured-product/<int:product_id>', methods=['POST'])
class AdminFeaturedProduct(Resource):
    @jwt_required()
    @admin_required()
    def post(self, product_id): # Add a product to the featured products        

        # Create a new featured product
        try:
            FeaturedProductService.add_featured_product(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product added to featured products successfully'}, 201

@product_ns.route('/admin/featured-product/<int:featured_product_id>', methods=['DELETE'])
class AdminFeaturedProduct(Resource):
    @jwt_required()
    @admin_required()
    def delete(self, featured_product_id): # Remove a product from the featured products
        print('featured_product_id', featured_product_id)
        try:
            FeaturedProductService.delete_featured_product(featured_product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product removed from featured products successfully'}, 200

# Define the routes for the product image operations
@product_ns.route('/admin/product-image/<int:product_id>', methods=['POST', 'GET'])
class AdminProductImageResource(Resource):
    @jwt_required()
    @admin_required()
    def post(self, product_id): # Add a product image for a product
        if 'image' not in request.files:
            return {'error': 'No image provided'}, 400
        
        image_file = request.files['image']

        # Get the image and upload it to Google Cloud Storage and get the image path
        try:
            image_path = ProductImageService.upload_product_image(image_file, product_id)

            # Create a new data object with the image path and product id
            new_data = {
                'image_path': image_path,
                'product_id': product_id
            }
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        # Validate the request data
        try:
            valid_data = product_image_schema.load(new_data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Create a new product image
        try:
            ProductImageService.create_product_image(valid_data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product image created successfully'}, 201

    @jwt_required()
    def get(self, product_id):
        try:
            product_images = ProductImageService.get_all_product_images(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        try:
            product_images = product_image_schema.dump(product_images, many=True) # Serialize the product images
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return marshal(product_images, product_image_model), 200

@product_ns.route('/admin/product-image/<int:product_image_id>', methods=['DELETE'])
class AdminProductImageResource(Resource):
    @jwt_required()
    @admin_required()
    def delete(self, product_image_id): # Delete a product image for a product
        try:
            ProductImageService.delete_product_image(product_image_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product image deleted successfully'}, 200
