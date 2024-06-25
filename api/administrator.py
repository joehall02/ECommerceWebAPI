from marshmallow import Schema, fields as ma_fields, ValidationError
from models import Order, Product, ProductImage, Category, FeaturedProduct
from flask import request
from flask_restx import Namespace, Resource, fields
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

        return categories
    
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

@admin_ns.route('/category', methods=['POST', 'GET'])
class CategoryResource(Resource):
    @admin_ns.marshal_list_with(category_model)
    @jwt_required()
    def get(self):        
        try:            
            categories = CategoryService.get_categories()
        except Exception as e:
            return {'message': str(e)}, 500
        
        try:
            categories = category_schema.dump(categories, many=True) # Serialize the categories, .dump() is used to serialize the data. many=True because it's a list, not a single object. 
        except ValidationError as e:
            return {'message': str(e)}, 500
        except Exception as e:
            return {'message': str(e)}, 500

        return categories, 200

    @admin_ns.expect(category_model)
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Validate the request data
        try:
            valid_data = category_schema.load(data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        # Create a new category
        try:
            CategoryService.create_category(valid_data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Category created successfully'}, 201

@admin_ns.route('/category/<int:category_id>', methods=['PUT', 'DELETE'])
class CategoryResource(Resource):
    @admin_ns.expect(category_model)
    @jwt_required()
    def put(self, category_id):
        data = request.get_json()

        # Validate the request data
        try:
            valid_data = category_schema.load(data, partial=True) # Allow partial category schema
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        # Update the category
        try:
            CategoryService.update_category(valid_data, category_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e: 
            return {'message': str(e)}, 500
        
        return {'message': 'Category updated successfully'}, 200

    @admin_ns.expect(category_model)
    @jwt_required()
    def delete(self, category_id):       
        # Delete the category
        try:
            CategoryService.delete_category(category_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Category deleted successfully'}, 200