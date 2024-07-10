from marshmallow import ValidationError
from models import Product, Category, FeaturedProduct, ProductImage
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from schemas import ProductSchema, ProductImageSchema, FeaturedProductSchema

# Define the schema instances
product_schema = ProductSchema()
featured_product_schema = FeaturedProductSchema()
product_image_schema = ProductImageSchema()

# Services    
class ProductService:
    @staticmethod
    def create_product(data):
        category = Category.query.get(data['category_id'])

        # Check category exists
        if not category:
            raise ValidationError('Category not found')

        new_product = Product(
            name = data['name'],
            description = data['description'],
            price = data['price'],
            stock = data['stock'],
            category_id = data['category_id']
        )

        new_product.save()

        return new_product

    @staticmethod
    def get_all_products():
        products = Product.query.all()

        # Check if there are any products
        if not products:
            raise ValidationError('No products found')

        return products
    
    @staticmethod
    def get_product(product_id):
        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')

        return product

    @staticmethod
    def update_product(data, product_id):
        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        # Check if data is empty
        if not data:
            raise ValidationError('No data provided')
        
        # Check if the category exists
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                raise ValidationError('Category not found')
        
        # Update product details
        # Loop through the data and update the product attributes using the key-value pairs in the data
        for key, value in data.items():
            setattr(product, key, value) 

        product.save()

        return product
        

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        product.delete()

        return product
    
class FeaturedProductService:
    @staticmethod
    def add_featured_product(product_id):
        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        featured_product = FeaturedProduct.query.filter_by(product_id=product_id).first()

        # Check if the product is already featured
        if featured_product:
            raise ValidationError('Product is already featured')
        
        new_featured_product = FeaturedProduct(
            product_id = product_id
        )

        new_featured_product.save()

        return new_featured_product
    
    @staticmethod
    def get_all_featured_products():
        featured_products = FeaturedProduct.query.all()

        # Check if there are any featured products
        if not featured_products:
            raise ValidationError('No featured products found')
        
        # Get the products associated with the featured products
        # List comprehension to add all products associated with each featured product to a list, similar to a for loop
        products = [featured_product.product for featured_product in featured_products] 

        return products
    
    @staticmethod
    def get_featured_product(featured_product_id):
        featured_product = FeaturedProduct.query.get(featured_product_id)

        # Check if the featured product exists
        if not featured_product:
            raise ValidationError('Featured product not found')
        
        # Get the product associated with the featured product
        product = featured_product.product

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        return product
    
    @staticmethod
    def delete_featured_product(featured_product_id):
        featured_product = FeaturedProduct.query.get(featured_product_id)

        # Check if the featured product exists
        if not featured_product:
            raise ValidationError('Featured product not found')
        
        featured_product.delete()

        return featured_product

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
@product_ns.route('/', methods=['POST', 'GET'])
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

    @jwt_required()
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
        
@product_ns.route('/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
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
    
    @jwt_required()
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
    def delete(self, product_id): # Delete a product
        # Delete the product
        try:
            ProductService.delete_product(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product deleted successfully'}, 200
    
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

@product_ns.route('/featured-product/<int:product_id>', methods=['POST'])
class FeaturedProductResource(Resource):
    @jwt_required()
    def post(self, product_id): # Add a product to the featured products        
        try:
            FeaturedProductService.add_featured_product(product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product added to featured products successfully'}, 201

@product_ns.route('/featured-product/<int:featured_product_id>', methods=['GET', 'DELETE'])
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

    @jwt_required()
    def delete(self, featured_product_id): # Remove a product from the featured products
        try:
            FeaturedProductService.delete_featured_product(featured_product_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Product removed from featured products successfully'}, 200
