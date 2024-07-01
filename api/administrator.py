from marshmallow import Schema, fields as ma_fields, ValidationError
from models import Order, Product, ProductImage, Category, FeaturedProduct
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required

# Define the schema for the models used to validate the request data
class CategorySchema(Schema):
    name = ma_fields.String(required=True, error_messages={'required': 'Category name is required', 'null': 'Category name cannot be empty'})

class ProductSchema(Schema):
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    description = ma_fields.String(required=True, error_messages={'required': 'Product description is required', 'null': 'Product description cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Product price is required', 'null': 'Product price cannot be empty'})
    stock = ma_fields.Integer(required=True, error_messages={'required': 'Product stock is required', 'null': 'Product stock cannot be empty'})
    category_id = ma_fields.Integer(required=True, error_messages={'required': 'Category ID is required', 'null': 'Category ID cannot be empty'})

class FeaturedProductSchema(Schema):
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})

class OrderSchema(Schema):
    order_date = ma_fields.DateTime(required=True, error_messages={'required': 'Order date is required', 'null': 'Order date cannot be empty'})
    total_price = ma_fields.Decimal(required=True, error_messages={'required': 'Total price is required', 'null': 'Total price cannot be empty'})
    status = ma_fields.String(required=True, error_messages={'required': 'Status is required', 'null': 'Status cannot be empty'})
    user_id = ma_fields.Integer(required=True, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})
    address_id = ma_fields.Integer(required=True, error_messages={'required': 'Address ID is required', 'null': 'Address ID cannot be empty'})
    payment_id = ma_fields.Integer(required=True, error_messages={'required': 'Payment ID is required', 'null': 'Payment ID cannot be empty'})

class ProductImageSchema(Schema):
    image_path = ma_fields.String(required=True, error_messages={'required': 'Image path is required', 'null': 'Image path cannot be empty'})
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})

# Define the schema instances
category_schema = CategorySchema()
product_schema = ProductSchema()
featured_product_schema = FeaturedProductSchema()
order_schema = OrderSchema()
product_image_schema = ProductImageSchema()

# Services
class CategoryService:
    @staticmethod
    def create_category(data):
        category_exists = Category.query.filter_by(name=data['name']).first()

        # Check if a category with the provided name already exists
        if category_exists:
            raise ValidationError('Category with the provided name already exists')
        
        new_category = Category(
            name = data['name']
        )
        new_category.save()
        return new_category
    
    @staticmethod
    def get_categories():
        categories = Category.query.all()

        # Check if there are any categories
        if not categories:
            raise ValidationError('No categories found')

        return categories
    
    @staticmethod
    def get_all_products_in_category(category_id):
        category = Category.query.get(category_id)

        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        products = category.products

        # Check if the category has any products
        if not products:
            raise ValidationError('No products found in the category')

        return products

    @staticmethod
    def update_category(data, category_id):
        category = Category.query.get(category_id)
        
        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        # Update the category name
        category.name = data['name']
        category.save()
        return category
    
    @staticmethod
    def delete_category(category_id):
        category = Category.query.get(category_id)
        
        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        category.delete()
        return category
    
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
        


admin_ns = Namespace('admin', description='Administrator operations')

# Define the models used for api documentation,
# actual validation is done using the schema
category_model = admin_ns.model('Category', {
    'name': fields.String(required=True),
})

product_model = admin_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True),
    'category_id': fields.Integer(required=True),
})

featured_product_model = admin_ns.model('FeaturedProduct', {
    'product_id': fields.Integer(required=True),
})

order_model = admin_ns.model('Order', {
    'order_date': fields.DateTime(required=True),
    'total_price': fields.Float(required=True),
    'status': fields.String(required=True),
    'user_id': fields.Integer(required=True),
    'address_id': fields.Integer(required=True),
    'payment_id': fields.Integer(required=True),
})

product_image_model = admin_ns.model('ProductImage', {
    'image_path': fields.String(required=True),
    'product_id': fields.Integer(required=True),
})


# Define the routes for the administrator operations

# Define Category routes for category operations
@admin_ns.route('/category', methods=['POST', 'GET'])
class CategoryResource(Resource):
    @jwt_required()
    def get(self): # Get all categories       
        try:            
            categories = CategoryService.get_categories()
        except Exception as e:
            return {'error': str(e)}, 500
        
        try:
            categories = category_schema.dump(categories, many=True) # Serialize the categories, .dump() is used to serialize the data. many=True because it's a list, not a single object. 
        except ValidationError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': str(e)}, 500

        return marshal(categories, category_model), 200

    @jwt_required()
    def post(self): # Create new category
        data = request.get_json()

        # Validate the request data
        try:
            valid_data = category_schema.load(data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Create a new category
        try:
            CategoryService.create_category(valid_data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Category created successfully'}, 201

@admin_ns.route('/category/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
class CategoryResource(Resource):
    @jwt_required()
    def get(self, category_id): # Get all products in a category
        # Get all products in the category
        try:
            products = CategoryService.get_all_products_in_category(category_id)                    
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Serialize the products
        try:
            products = product_schema.dump(products, many=True) # Serialize the products
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500                
        
        return marshal(products, product_model), 200

    @jwt_required()
    def put(self, category_id): # Edit category
        data = request.get_json()

        # Validate the request data
        try:
            valid_data = category_schema.load(data, partial=True) # Allow partial category schema
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Update the category
        try:
            CategoryService.update_category(valid_data, category_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e: 
            return {'error': str(e)}, 500
        
        return {'message': 'Category updated successfully'}, 200

    @jwt_required()
    def delete(self, category_id): # Delete a category      
        # Delete the category
        try:
            CategoryService.delete_category(category_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Category deleted successfully'}, 200
    
# Define Product routes for product operations
@admin_ns.route('/product', methods=['POST', 'GET'])
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
        
@admin_ns.route('/product/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
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
@admin_ns.route('/featured-product', methods=['GET'])
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

@admin_ns.route('/featured-product/<int:product_id>', methods=['POST'])
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

@admin_ns.route('/featured-product/<int:featured_product_id>', methods=['GET', 'DELETE'])
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
