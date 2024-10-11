from marshmallow import ValidationError
from models import Product, Category, FeaturedProduct, ProductImage

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