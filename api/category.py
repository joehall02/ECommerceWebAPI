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
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
})

product_model = category_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True),
    'category_id': fields.Integer(required=True),
})

@category_ns.route('/', methods=['GET'])
class CategoryResource(Resource):
    @handle_exceptions
    def get(self): # Get all categories                 
        categories = CategoryService.get_all_categories()        

        return marshal(categories, category_model), 200

@category_ns.route('/<int:category_id>', methods=['GET'])
class CategoryResource(Resource):
    @handle_exceptions
    def get(self, category_id): # Get category details
        category = CategoryService.get_category(category_id)

        return marshal(category, category_model), 200
    
    
    # def get(self, category_id): # Get all products in a category        
    #     products = CategoryService.get_all_products_in_category(category_id)                        
                         
    #     return marshal(products, product_model), 200

@category_ns.route('/admin', methods=['POST', 'GET'])
class AdminCategoryResource(Resource):
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def post(self): # Create new category
        data = request.get_json()
                
        CategoryService.create_category(data)        
        
        return {'message': 'Category created successfully'}, 201
    
    @jwt_required()
    @admin_required()
    @handle_exceptions
    def get(self): # Get all categories               
        page = request.args.get('page', 1, type=int) # Get the page number from the query string

        results = CategoryService.get_categories(page) 

        response = {
            'categories': marshal(results['categories'], category_model),
            'total_pages': results['total_pages'],
            'current_page': results['current_page'],
            'total_categories': results['total_categories']
        }

        return response, 200
    
@category_ns.route('/admin/<int:category_id>', methods=['PUT', 'DELETE'])
class AdminCategoryResource(Resource):
    # @jwt_required()
    # @admin_required()
    # @handle_exceptions
    # def get(self, category_id): # Get category details
    #     category = CategoryService.get_category(category_id)

    #     return marshal(category, category_model), 200

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