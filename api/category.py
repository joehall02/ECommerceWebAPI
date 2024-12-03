from marshmallow import ValidationError
from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from decorators import admin_required
from services.category_service import CategoryService
from decorators import handle_exceptions
    
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
    @handle_exceptions
    def get(self): # Get all categories                 
        categories = CategoryService.get_categories()        

        return marshal(categories, category_model), 200

@category_ns.route('/<int:category_id>', methods=['GET'])
class CategoryResource(Resource):
    @jwt_required()
    @handle_exceptions
    def get(self, category_id): # Get all products in a category        
        products = CategoryService.get_all_products_in_category(category_id)                        
                         
        return marshal(products, product_model), 200

@category_ns.route('/admin', methods=['POST'])
class AdminCategoryResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def post(self): # Create new category
        data = request.get_json()
                
        CategoryService.create_category(data)        
        
        return {'message': 'Category created successfully'}, 201
    
@category_ns.route('/admin/<int:category_id>', methods=['PUT', 'DELETE'])
class AdminCategoryResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def put(self, category_id): # Edit category
        data = request.get_json()
                
        CategoryService.update_category(data, category_id)        
        
        return {'message': 'Category updated successfully'}, 200

    @jwt_required()
    @admin_required()
    @handle_exceptions
    def delete(self, category_id): # Delete a category              
        CategoryService.delete_category(category_id)        
        
        return {'message': 'Category deleted successfully'}, 200