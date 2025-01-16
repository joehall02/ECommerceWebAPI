import uuid
from marshmallow import ValidationError
from models import Product, Category, FeaturedProduct, ProductImage
from werkzeug.utils import secure_filename
from google.cloud import storage
from dotenv import load_dotenv
from schemas import ProductSchema, ProductImageSchema, FeaturedProductSchema, ProductShopSchema, ProductAdminSchema
import os
import stripe

# Load environment variables
load_dotenv()

# Define the schema instances
product_schema = ProductSchema()
featured_product_schema = FeaturedProductSchema()
product_image_schema = ProductImageSchema()
product_shop_schema = ProductShopSchema()
product_admin_schema = ProductAdminSchema()

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

        # Check if the price is a negative number
        if valid_data['price'] < 0:
            raise ValidationError('Price cannot be a negative number')

        category = Category.query.get(data['category_id'])

        # Check category exists
        if not category:
            raise ValidationError('Category not found')

        # Make product locally
        new_product = Product(
            name = valid_data['name'],
            description = valid_data['description'],
            price = valid_data['price'],
            stock = valid_data['stock'],
            category_id = valid_data['category_id']
        )

        new_product.save()

        try:
            # Create product in stripe
            stripe_product = stripe.Product.create(
                name=new_product.name,
                description=new_product.description,
                metadata={
                    'product_id': new_product.id # Track local product id in stripe
                }
            )

            # Create price in stripe
            stripe_price = stripe.Price.create(
                unit_amount=int(new_product.price * 100), # Convert price to pence
                currency='gbp', # Set currency to GBP
                product=stripe_product.id
            )

            # Update the product with the stripe product and price ids
            new_product.stripe_product_id = stripe_product.id
            new_product.stripe_price_id = stripe_price.id

            new_product.save()

        except Exception as e:
            new_product.delete()
            raise ValidationError(f"Failed to create product in Stripe: {str(e)}")

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
            image_path = product.product_images[0].image_path if product.product_images else None # Get the first image path if it exists
            product_data = {
                'id': product.id,
                'name': product.name,                
                'price': product.price,                                
                'image_path': image_path,
                'category_name': product.category.name
            }
            product_list.append(product_data)
        
        # Serialize the data
        products = product_shop_schema.dump(product_list, many=True)

        return products
    
    @staticmethod
    def get_all_admin_products():
        products = Product.query.all()

        # Check if there are any products
        if not products:
            raise ValidationError('No products found')
        
        # Serialize the data
        products = product_admin_schema.dump(products, many=True)

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

        # Check if name is provided, if so, update the stripe product
        if 'name' in valid_data:
            try:
                stripe.Product.modify(
                    product.stripe_product_id,
                    name=valid_data['name']                    
                )
            except Exception as e:
                raise ValidationError(f"Failed to update product in Stripe: {str(e)}")

        # Check if description is provided, if so, update the stripe product
        if 'description' in valid_data:
            try:
                stripe.Product.modify(
                    product.stripe_product_id,
                    description=valid_data['description']                    
                )
            except Exception as e:
                raise ValidationError(f"Failed to update product in Stripe: {str(e)}")

        # Check if price is provided, if so, update the stripe price
        if 'price' in valid_data:
            try:
                # Set the price to inactive in stripe
                stripe.Price.modify(
                    product.stripe_price_id,
                    active=False # Set the price to inactive
                )

                # Create a new price in stripe
                stripe_price = stripe.Price.create(
                    unit_amount=int(valid_data['price'] * 100), # Convert price to pence
                    currency='gbp', # Set currency to GBP
                    product=product.stripe_product_id
                )

                # Update the product with the new stripe price id
                product.stripe_price_id = stripe_price.id

            except Exception as e:
                raise ValidationError(f"Failed to update price in Stripe: {str(e)}")

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
        
        # Get the product images
        product_images = ProductImage.query.filter_by(product_id=product_id).all()

        # Loop through the product images and remove them from Google Cloud Storage
        for product_image in product_images:
            remove_image_from_google_cloud_storage(product_image.image_path)                

        # Delete the product
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

         # Prepare the data to be serialized
        product_list = []
        
        for product in products:
            image_path = product.product_images[0].image_path if product.product_images else None # Get the first image path if it exists
            product_data = {
                'id': product.id,
                'name': product.name,                
                'price': product.price,                                
                'image_path': image_path,
                'category_name': product.category.name
            }
            product_list.append(product_data)

        # Serialize the data
        featured_products = product_shop_schema.dump(product_list, many=True)

        return featured_products
    
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
    def check_featured_product(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')        

        featured_product = FeaturedProduct.query.filter_by(product_id=product_id).first()
        
        # Check if the product is featured
        if not featured_product:
            raise ValidationError('Product is not featured')
        
        # Serialize the data
        featured_product = featured_product_schema.dump(featured_product)

        return featured_product
    
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

        # Upload the image file to Stripe product
        stripe.Product.modify(
            product.stripe_product_id,
            images=["https://storage.googleapis.com/" + image_path]
        )

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
        
        # Check if the product already has an image
        product_image = ProductImage.query.filter_by(product_id=valid_data['product_id']).first()

        # if product_image exists, delete the image and create a new one
        if product_image:
            remove_image_from_google_cloud_storage(product_image.image_path)
            product_image.delete()
        
        new_product_image = ProductImage(
            image_path = valid_data['image_path'],
            product_id = valid_data['product_id']
        )

        new_product_image.save()

        return new_product_image

    def get_product_image(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')
        
        product_image = ProductImage.query.filter_by(product_id=product_id).first()

        # Check if there are any product images
        if not product_image:
            raise ValidationError('No product image found')
        
        # Serialize the data
        product_image = product_image_schema.dump(product_image)
        
        return product_image

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
