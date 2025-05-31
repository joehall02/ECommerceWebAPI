from marshmallow import ValidationError
from models import Product, Category, FeaturedProduct, ProductImage
from werkzeug.utils import secure_filename
from schemas import ProductSchema, ProductImageSchema, FeaturedProductSchema, ProductShopSchema, ProductAdminSchema
from services.utils import allowed_file, upload_image_to_google_cloud_storage, remove_image_from_google_cloud_storage, create_stripe_product_and_price, update_stripe_product_and_price, upload_image_to_stripe_product
from exts import cache

# Define the schema instances
product_schema = ProductSchema()
featured_product_schema = FeaturedProductSchema()
product_image_schema = ProductImageSchema()
product_shop_schema = ProductShopSchema()
product_admin_schema = ProductAdminSchema()

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

        # Create the product and price objects in Stripe
        create_stripe_product_and_price(new_product)

        # Clear the cache
        cache.delete_memoized(ProductService.get_all_products)
        cache.delete_memoized(ProductService.get_all_admin_products)

        return new_product

    @staticmethod    
    @cache.memoize(timeout=86400) # Cache the results for 24 hours
    def get_all_products(page=1, per_page=9, category_id=None, sort_by=None):
        print('Fetching products')
        query = Product.query.filter(Product.stock > 0) # Get all products with stock greater than 0
        
        # Check if a category id is provided
        if category_id:
            query = query.filter_by(category_id=category_id)

        # Apply sorting
        if sort_by == 'Name (A-Z)':
            query = query.order_by(Product.name.asc())
        elif sort_by == 'Name (Z-A)':
            query = query.order_by(Product.name.desc())
        elif sort_by == 'Price (Low to High)':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'Price (High to Low)':
            query = query.order_by(Product.price.desc())
        else:
            # Default sorting by id in descending order, i.e. latest products first
            query = query.order_by(Product.id.desc())

        products_query = query.paginate(page=page, per_page=per_page, error_out=False) # Paginate the query
        products = products_query.items

        # Check if there are any products
        # if not products:
        #     raise ValidationError('No products in stock at the moment. Please come back later!')
        
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

        return {
            'products': products,
            'total_pages': products_query.pages,
            'current_page': products_query.page,
            'total_products': products_query.total
        }
    
    @staticmethod
    @cache.memoize(timeout=86400) # Cache the results for 24 hours
    def get_all_admin_products(page=1, per_page=10, category_id=None):
        print('Fetching admin products')
        query = Product.query.order_by(Product.id.desc()) # Get all products in descending order of id (latest products first)

        if category_id:
            query = query.filter_by(category_id=category_id)

        # Paginate the query
        products_query = query.paginate(page=page, per_page=per_page, error_out=False)
        products = products_query.items

        # Check if there are any products
        if not products:
            raise ValidationError('No products found')
        
        # Serialize the data
        products = product_admin_schema.dump(products, many=True)

        return {
            'products': products,
            'total_pages': products_query.pages,
            'current_page': products_query.page,
            'total_products': products_query.total
        }

    @staticmethod
    def get_product(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

        product = Product.query.get(product_id)

        # Check if the product exists
        if not product:
            raise ValidationError('Product not found')

        # Serialise the data
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

        # Update the stripe product and price objects
        update_stripe_product_and_price(product, valid_data)
        
        if 'stock' in valid_data:
            # Check if the stock is a negative number
            if valid_data['stock'] < 0:
                raise ValidationError('Stock cannot be a negative number')
            
            # Check if the stock is less that the reserved stock
            if product.reserved_stock > valid_data['stock']:
                raise ValidationError('Stock cannot be less than the reserved stock')        

        # Update product details
        # Loop through the data and update the product attributes using the key-value pairs in the data
        for key, value in valid_data.items():
            setattr(product, key, value) 

        # Clear the cache
        cache.delete_memoized(ProductService.get_all_products)
        cache.delete_memoized(ProductService.get_all_admin_products)
        cache.delete_memoized(FeaturedProductService.get_all_featured_products)

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

        # Clear the cache
        cache.delete_memoized(ProductService.get_all_products)
        cache.delete_memoized(ProductService.get_all_admin_products)
        cache.delete_memoized(FeaturedProductService.get_all_featured_products)

        return product
    
class FeaturedProductService:
    @staticmethod
    def add_featured_product(product_id):
        # Check if the product id is provided
        if not product_id:
            raise ValidationError('No product id provided')

        # If theres already 4 featured products, return an error
        if len(FeaturedProduct.query.all()) >= 4:
            raise ValidationError('There are already 4 featured products')

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

        # Clear the cache
        cache.delete_memoized(FeaturedProductService.get_all_featured_products)

        return new_featured_product
    
    @staticmethod
    @cache.memoize(timeout=86400) # Cache the results for 24 hours
    def get_all_featured_products():
        print('Fetching featured products')
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
            # If products stock is 0, dont add it to the list
            if product.stock > 0:
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

        # Clear the cache
        cache.delete_memoized(FeaturedProductService.get_all_featured_products)

        return featured_product
    
class ProductImageService:
    @staticmethod
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

    @staticmethod    
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
        upload_image_to_stripe_product(product, image_path)

        data = {
            'image_path': image_path,
            'product_id': product_id
        }

        # Create a new product image
        new_product_image = ProductImageService.create_product_image(data)

        # Clear the cache
        cache.delete_memoized(ProductImageService.get_product_image)
        cache.delete_memoized(FeaturedProductService.get_all_featured_products)

        return new_product_image
    
    @staticmethod
    @cache.memoize(timeout=86400) # Cache the results for 24 hours
    def get_product_image(product_id):
        print('Fetching product image')
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

    # @staticmethod
    # def delete_product_image(product_image_id):
    #     # Check if the product image id is provided
    #     if not product_image_id:
    #         raise ValidationError('No product image id provided')

    #     product_image = ProductImage.query.get(product_image_id)

    #     # Check if the product image exists
    #     if not product_image:
    #         raise ValidationError('Product image not found')
        
    #     # Remove the image file from Google Cloud Storage
    #     remove_image_from_google_cloud_storage(product_image.image_path)        

    #     product_image.delete()

    #     # Clear the cache
    #     cache.delete_memoized(ProductImageService.get_product_image)

    #     return product_image
