import uuid
from flask import current_app
from marshmallow import ValidationError
from google.cloud import storage
import os
from itsdangerous import URLSafeTimedSerializer

import requests


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

def send_email(data):
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