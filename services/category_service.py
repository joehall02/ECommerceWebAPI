from marshmallow import ValidationError
from models import Category
from schemas import CategorySchema, ProductSchema
from services.utils import remove_image_from_google_cloud_storage # Used to delete product images from cloud bucket if admin deletes a category

# Define the schema instances
category_schema = CategorySchema()
product_schema = ProductSchema()

# Services
class CategoryService:
    @staticmethod
    def create_category(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the category schema
        valid_data = category_schema.load(data)

        category = Category.query.filter_by(name=data['name']).first()

        # Check if a category with the provided name already exists
        if category:
            raise ValidationError('Category with the provided name already exists')
        
        new_category = Category(
            name = valid_data['name']
        )
        new_category.save()
        return new_category
    
    @staticmethod
    def get_categories(page=1, per_page=10):
        # Paginate the categories. Order by id in descending order to get the latest categories first
        categories_query = Category.query.order_by(Category.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        categories = categories_query.items

        # Check if there are any categories
        if not categories:
            raise ValidationError('No categories found')

        # Serialize the categories, .dump() is used to serialize the data. many=True because it's a list, not a single object. 
        categories = category_schema.dump(categories, many=True)

        return {
            'categories': categories,
            'total_pages': categories_query.pages,
            'current_page': categories_query.page,
            'total_categories': categories_query.total
        }
    
    @staticmethod
    def get_all_categories():
        categories = Category.query.all()

        # Check if there are any categories
        if not categories:
            raise ValidationError('No categories found')

        # Serialize the categories, .dump() is used to serialize the data. many=True because it's a list, not a single object. 
        categories = category_schema.dump(categories, many=True)

        return categories
    
    @staticmethod
    def get_category(category_id):
        category = Category.query.get(category_id)

        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        # Serialize the category
        category = category_schema.dump(category)

        return category
    
    @staticmethod
    def get_all_products_in_category(category_id):
        # Check if the category id is provided
        if not category_id:
            raise ValidationError('No category id provided')
        
        category = Category.query.get(category_id)

        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        products = category.products

        # Check if the category has any products
        if not products:
            raise ValidationError('No products found in the category')
        
        # Serialize the products
        products = product_schema.dump(products, many=True)

        return products

    @staticmethod
    def update_category(data, category_id):
        # Check if the category id is provided
        if not category_id:
            raise ValidationError('No category id provided')
        
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the category schema
        valid_data = category_schema.load(data, partial=True) # Allow partial category schema

        category = Category.query.get(category_id)
        
        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        # Update the category name
        category.name = valid_data['name']
        category.save()
        return category
    
    @staticmethod
    def delete_category(category_id):
        # Check if the category id is provided
        if not category_id:
            raise ValidationError('No category id provided')

        category = Category.query.get(category_id)
        
        # Check if the category exists
        if not category:
            raise ValidationError('Category not found')
        
        # Get all products in the category
        products = category.products

        # Check if the category has any products
        if products:
            # Delete each product image from Google Cloud Storage
            for product in products:
                product_images = product.product_images
                for product_image in product_images:
                    remove_image_from_google_cloud_storage(product_image.image_path)
        
        category.delete()
        return category