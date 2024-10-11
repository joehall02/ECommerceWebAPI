from marshmallow import ValidationError
from models import Category

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