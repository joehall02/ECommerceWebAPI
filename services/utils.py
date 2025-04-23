import uuid
from flask import current_app
from marshmallow import ValidationError
from google.cloud import storage
from itsdangerous import URLSafeTimedSerializer
from models import User
import requests
import stripe


# Check if the file is an image
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# Upload an image file to Google Cloud Storage
def upload_image_to_google_cloud_storage(image_file):
    try:
        # Set the Google Cloud Storage bucket name
        bucket_name = current_app.config['GOOGLE_CLOUD_STORAGE_BUCKET_NAME']

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
    except Exception as e:
        raise ValidationError(f'Error uploading image to Google Cloud Storage: {str(e)}')

# Remove an image file from Google Cloud Storage
def remove_image_from_google_cloud_storage(image_path):
    try:
        # Set the Google Cloud Storage bucket name
        bucket_name = current_app.config['GOOGLE_CLOUD_STORAGE_BUCKET_NAME']

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
    except Exception as e:
        raise ValidationError(f'Error removing image from Google Cloud Storage: {str(e)}')

def send_email(data):
    try:
        print("Sending email")

        url = f"https://api.mailgun.net/v3/{current_app.config['MAILGUN_DOMAIN_NAME']}/messages"
        auth = ("api", current_app.config['MAILGUN_API_KEY'])
        data = {
            "from": f"{current_app.config['MAILGUN_SENDER_EMAIL']}",
            "to": f"{data['to_name']} <{data['to_email']}>",
            "subject": data['subject'],
            "text": data['text']
        }

        response = requests.post(url, auth=auth, data=data)

        # Print the response status code and text for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code != 200:
            raise Exception(f"Failed to send email: {response.text}")

        return response.json()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise ValidationError(f"Error sending email")

def send_contact_us_email(data):
    try:
        print("Sending contact us email")
        
        url = f"https://api.mailgun.net/v3/{current_app.config['MAILGUN_DOMAIN_NAME']}/messages"
        auth = ("api", current_app.config['MAILGUN_API_KEY'])
        data = {
            "from": f"{data['from_name']} <{data['from_email']}>",
            "to": f"{current_app.config['CONTACT_US_EMAIL']}",
            "subject": f"Contact us: {data['subject']}",
            "text": data['message']
        }

        response = requests.post(url, auth=auth, data=data)

        # Print the response status code and text for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code != 200:
            raise Exception(f"Failed to send email: {response.text}")
        
        return response.json()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise ValidationError(f"Error sending email")

# Generate a verification token using the email as the unique identifier
def generate_verification_token(email):
    # Create a URLSafeTimedSerializer object using the secret key
    serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    # Generate the token using the email and the security salt
    token = serialiser.dumps(email, salt=current_app.config['SECURITY_SALT'])

    return token

# Verify the verification token, expire the token after 3600 seconds (1 hour)
def verify_token(token, expiration=3600):
    # Create a URLSafeTimedSerializer object using the secret key
    serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    # Verify the token using the security salt and the expiration time
    try:
        email = serialiser.loads(token, salt=current_app.config['SECURITY_SALT'], max_age=expiration)
    except:
        return None
    
    return email

# Create stripe product and price objects
def create_stripe_product_and_price(new_product):
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
        print(f"Failed to create product in Stripe: {str(e)}")
        raise ValidationError(f"Failed to create product in Stripe: {str(e)}")

def update_stripe_product_and_price(product, valid_data):
    # Check if name is provided, if so, update the stripe product
    if 'name' in valid_data:
        try:
            stripe.Product.modify(
                product.stripe_product_id,
                name=valid_data['name']                    
            )
        except Exception as e:
            raise ValidationError(f"Failed to update product name in Stripe: {str(e)}")

    # Check if description is provided, if so, update the stripe product
    if 'description' in valid_data:
        try:
            stripe.Product.modify(
                product.stripe_product_id,
                description=valid_data['description']                    
            )
        except Exception as e:
            raise ValidationError(f"Failed to update product description in Stripe: {str(e)}")

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
        
# Upload image to stripe product
def upload_image_to_stripe_product(product, image_path):
    try :
        stripe.Product.modify(
            product.stripe_product_id,
            images=["https://storage.googleapis.com/" + image_path]
        )
    except Exception as e:
        raise ValidationError(f"Failed to upload image to Stripe product: {str(e)}")
    
# Create a stripe checkout session
def create_stripe_checkout_session(user, valid_data, line_items):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'{current_app.config['FRONTEND_URL']}/checkout/success',
            cancel_url=f'{current_app.config['FRONTEND_URL']}/checkout/cancel',
            customer_email=user.email if not user.stripe_customer_id else None, # Attach the email to the session if the user doesn't have a stripe customer id
            customer=user.stripe_customer_id if user.stripe_customer_id else None, # Attach the customer to the session if one exists
            customer_creation='always' if not user.stripe_customer_id else None, # Create a new customer if one doesn't exist

            metadata={
                'user_id': user.id,
                'full_name': valid_data['full_name'],
                'address_line_1': valid_data['address_line_1'],
                'address_line_2': valid_data['address_line_2'] if 'address_line_2' in valid_data else None,
                'city': valid_data['city'],
                'postcode': valid_data['postcode'],
            }
        )

        return session
    except Exception as e:
        print(f"Failed to create Stripe checkout session: {str(e)}")
        raise ValidationError(f"Failed to create Stripe checkout session")

# Stripe webhook handler
def stripe_webhook_handler(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe.webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return {'error': str(e)}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return {'error': str(e)}, 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object'] # Contains a stripe checkout session            
        customer_email = session['customer_details']['email']

        # Extract the metadata, which contains the user id and address details
        metadata = session['metadata']
        user_id = metadata['user_id']
        full_name = metadata['full_name']
        address_line_1 = metadata['address_line_1']
        address_line_2 = metadata['address_line_2']
        city = metadata['city']
        postcode = metadata['postcode']

        
        # Create a new order
        data = {
            'user_id': user_id,
            'full_name': full_name,
            'address_line_1': address_line_1,
            'address_line_2': address_line_2,
            'city': city,
            'postcode': postcode,
            'customer_email': customer_email
        }

        # Extract the stripe customer id
        stripe_customer_id = session['customer']

        user = User.query.get(user_id)

        if user:
            user.stripe_customer_id = stripe_customer_id
            user.save()

        return data

    return None # Return None if the event type is not recognised