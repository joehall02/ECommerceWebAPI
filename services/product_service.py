import uuid
from marshmallow import ValidationError
from models import Product, Category, FeaturedProduct, ProductImage
from werkzeug.utils import secure_filename
from google.cloud import storage
from dotenv import load_dotenv
from schemas import ProductSchema, ProductImageSchema, FeaturedProductSchema, ProductShopSchema
import os

# Load environment variables
load_dotenv()

# Define the schema instances
product_schema = ProductSchema()
featured_product_schema = FeaturedProductSchema()
product_image_schema = ProductImageSchema()
product_shop_schema = ProductShopSchema()

# Check if the file is an image
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# Upload an image file to Google Cloud Storage
def upload_image_to_google_cloud_storage(image_file):
    # Set the Google Cloud Storage bucket name
    bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET_NAME')

    if not bucket_name:
        raise ValidationError('Google Cloud Storage bucket name not found')

    # Intialise a Google Cloud Storage client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Create a unique filename for the image file
    image_file.filename = f"{uuid.uuid4().hex}-{image_file.filename}"

    # Create a blob object
    blob = bucket.blob(image_file.filename)

    # Upload the image file to Google Cloud Storage
    blob.upload_from_string(image_file.read(), content_type=image_file.content_type)

    # Get the image path
    image_path = f'{bucket_name}/{blob.name}'

    return image_path

# Remove an image file from Google Cloud Storage
def remove_image_from_google_cloud_storage(image_path):
    # Set the Google Cloud Storage bucket name
    bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET_NAME')

    # Check if the bucket name exists
    if not bucket_name:
        raise ValidationError('Google Cloud Storage bucket name not found')

    # Intialise a Google Cloud Storage client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Get the image path without the bucket name
    image_path = image_path.split(f'{bucket_name}/')[1]

    # Get the blob
    blob = bucket.blob(image_path)

    # Delete the image file from Google Cloud Storage
    blob.delete()

# Services    
class ProductService:
    @staticmethod
    def create_product(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data using the schema
        valid_data = product_schema.load(data)

        category = Category.query.get(data['category_id'])

        # Check category exists
        if not category:
            raise ValidationError('Category not found')

        new_product = Product(
            name = valid_data['name'],
            description = valid_data['description'],
            price = valid_data['price'],
            stock = valid_data['stock'],
            category_id = valid_data['category_id']
        )

        new_product.save()

        return new_product

    @staticmethod
    def get_all_products():
        products = Product.query.all()

        # Check if there are any products
        if not products:
            raise ValidationError('No products found')
        
        # Prepare the data to be serialized
        product_list = []
        
        for product in products:
            image_path = product.product_images[0].image_path if product.product_images else None
            product_data = {
                'product_id': product.id,
                'name': product.name,                
                'price': product.price,                                
                'image_path': image_path
            }
            product_list.append(product_data)
        
        # Serialize the data
        products = product_shop_schema.dump(product_list, many=True)

        return products
    
    @staticmethod
    def get_product(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')

        # Serialize the data
        product = product_schema.dump(product)

        return product

    @staticmethod
    def update_product(data, product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')
        
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data using the schema
        valid_data = product_schema.load(data, partial=True)

        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        # Check if data is empty
        if not valid_data:
            raise ValidationError('No data provided')
        
        # Check if the category exists
        if 'category_id' in valid_data:
            category = Category.query.get(valid_data['category_id'])
            if not category:
                raise ValidationError('Category not found')
        
        # Update product details
        # Loop through the data and update the product attributes using the key-value pairs in the data
        for key, value in valid_data.items():
            setattr(product, key, value) 

        product.save()

        return product
        

    @staticmethod
    def delete_product(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        product.delete()

        return product
    
class FeaturedProductService:
    @staticmethod
    def add_featured_product(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

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

        # Serialize the data
        featured_products = product_schema.dump(featured_products, many=True)

        return products
    
    @staticmethod
    def get_featured_product(featured_product_id):
        # Check if the featured product id is provided
        if not featured_product_id:
            raise ValidationError('No featured product id provided')

        featured_product = FeaturedProduct.query.get(featured_product_id)

        # Check if the featured product exists
        if not featured_product:
            raise ValidationError('Featured product not found')
        
        # Get the product associated with the featured product
        product = featured_product.product

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        # Serialize the data
        featured_product = product_schema.dump(featured_product)
        
        return product
    
    @staticmethod
    def delete_featured_product(featured_product_id):
        # Check if the featured product id is provided
        if not featured_product_id:
            raise ValidationError('No featured product id provided')

        featured_product = FeaturedProduct.query.get(featured_product_id)

        # Check if the featured product exists
        if not featured_product:
            raise ValidationError('Featured product not found')
        
        featured_product.delete()

        return featured_product
    
class ProductImageService:
    def upload_product_image(image_file, product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')
        
        # Ensure the image file is not empty
        if not image_file:
            raise ValidationError('No image file provided')
        
        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        # Ensure the filename is secure
        image_file.filename = secure_filename(image_file.filename)

        # Ensure the image file is an image
        if not allowed_file(image_file.filename):
            raise ValidationError('Invalid image file')

        # Upload the image file to Google Cloud Storage
        image_path = upload_image_to_google_cloud_storage(image_file)

        return image_path    

    def create_product_image(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data using the schema
        valid_data = product_image_schema.load(data)

        product = Product.query.get(valid_data['product_id'])

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        new_product_image = ProductImage(
            image_path = valid_data['image_path'],
            product_id = valid_data['product_id']
        )

        new_product_image.save()

        return new_product_image

    def get_all_product_images(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        product_images = ProductImage.query.filter_by(product_id=product_id).all()

        # Check if there are any product images
        if not product_images:
            raise ValidationError('No product images found')
        
        # Serialize the data
        product_images = product_image_schema.dump(product_images, many=True)
        
        return product_images

    def delete_product_image(product_image_id):
        # Check if the product image id is provided
        if not product_image_id:
            raise ValidationError('No product image id provided')

        product_image = ProductImage.query.get(product_image_id)

        # Check if the product image exists
        if not product_image:
            raise ValidationError('Product image not found')
        
        # Remove the image file from Google Cloud Storage
        remove_image_from_google_cloud_storage(product_image.image_path)
        
        product_image.delete()

        return product_image
