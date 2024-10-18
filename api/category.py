from marshmallow import ValidationError
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from decorators import admin_required
from services.category_service import CategoryService
    
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
        except ValidationError as e:
            return {'error': str(e)}, 400
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
                         
        return marshal(products, product_model), 200

@category_ns.route('/admin', methods=['POST'])
class AdminCategoryResource(Resource):
    @jwt_required()
    @admin_required()
    def post(self): # Create new category
        data = request.get_json()
        
        # Create a new category
        try:
            CategoryService.create_category(data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Category created successfully'}, 201
    
@category_ns.route('/admin/<int:category_id>', methods=['PUT', 'DELETE'])
class AdminCategoryResource(Resource):
    @jwt_required()
    @admin_required()
    def put(self, category_id): # Edit category
        data = request.get_json()
        
        # Update the category
        try:
            CategoryService.update_category(data, category_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e: 
            return {'error': str(e)}, 500
        
        return {'message': 'Category updated successfully'}, 200

    @jwt_required()
    @admin_required()
    def delete(self, category_id): # Delete a category      
        # Delete the category
        try:
            CategoryService.delete_category(category_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Category deleted successfully'}, 200