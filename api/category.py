from marshmallow import ValidationError
from models import Category
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from schemas import CategorySchema, ProductSchema

# Define the schema instances
category_schema = CategorySchema()
product_schema = ProductSchema()

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
    
# Define the namespace
category_ns = Namespace('category', description='Category operations')

# Define the models used for api documentation,
# actual validation is done using the schema
category_model = category_ns.model('Category', {
    'name': fields.String(required=True),
})

product_model = category_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True),
    'category_id': fields.Integer(required=True),
})

# Define the routes for category operations
@category_ns.route('/', methods=['GET'])
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

@category_ns.route('/<int:category_id>', methods=['GET'])
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

@category_ns.route('/admin', methods=['POST'])
class AdminCategoryResource(Resource):
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
    
@category_ns.route('/admin/<int:category_id>', methods=['PUT', 'DELETE'])
class AdminCategoryResource(Resource):
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