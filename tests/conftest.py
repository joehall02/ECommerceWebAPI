import io
from flask_jwt_extended import get_jwt_identity
import pytest
from main import create_app
from config import Test
from exts import db, limiter, cache
from werkzeug.security import generate_password_hash
from datetime import datetime
from zoneinfo import ZoneInfo
from models import User, Cart
from sqlalchemy.orm import scoped_session, sessionmaker

# Create a fixture to create an instance of the app
@pytest.fixture(scope='session') # This fixture will be called only once for the session
def test_app():
    # Create an instance of the app with the test configuration
    app = create_app(Test)

    # Use the app context
    with app.app_context():
        # Drop all the database tables
        db.drop_all()

        # Create the database tables
        db.create_all()

        # Yield the app
        yield app

        # Remove the session
        db.session.remove()

        # Drop the database tables
        db.drop_all()
    
    return app

# Create a new database session for each test and rollback the session after the test
@pytest.fixture(scope='function', autouse=True) # This fixture will be called for each test function
def db_session(test_app):
    # Create a connection to the database
    connection = db.engine.connect()

    # Begin a transaction
    transaction = connection.begin()

    # Create a new session factory bound to the connection
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)

    # Override the default db session
    db.session = session

    # Yield the session to your tests
    yield session

    # Cleanup: remove the session and rollback the transaction
    session.remove()  # Close the session
    transaction.rollback()  # Rollback any changes made during the test
    connection.close()  # Close the connection

# Flask test client to be used in the tests
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

# Missing data fixture
@pytest.fixture()
def missing_data():
    return {}

# Clear cache after each test
@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

# Auth Fixtures

# Create a fixture to create a test user
@pytest.fixture 
def test_create_users(db_session):
    # Create an admin user and cart
    admin = User (
        full_name = 'John Doe',
        email = 'admin@test.com',
        password = generate_password_hash('password123'),
        role = 'admin',
        created_at = datetime.now(tz=ZoneInfo("UTC")),
        is_verified = True
    )
    db.session.add(admin)
    db.session.flush()

    cart = Cart (
        user_id = admin.id
    )
    db.session.add(cart)
    db.session.flush()

    # Create a customer user and cart
    customer = User (
        full_name = 'Jane Doe',
        email = 'customer@test.com',
        password = generate_password_hash('password123'),
        role = 'customer',
        created_at = datetime.now(tz=ZoneInfo("UTC")),
        is_verified = True
    )
    db.session.add(customer)
    db.session.flush()
    
    cart = Cart (
        user_id = customer.id
    )
    db.session.add(cart)
    db.session.flush()

    return admin, customer

@pytest.fixture
def test_customer_login(test_client, test_create_users):    
    response = test_client.post('/user/login', json={
        'email': 'customer@test.com',
        'password': 'password123',
        'remember_me': False
    })

    # Check if the response is valid
    assert response.status_code == 200

    # Extract cookies from the response headers
    cookies = response.headers.getlist('Set-Cookie')
    
    return cookies

# @pytest.fixture()
# def create_test_guest_user(db_session):
#     guest = User (
#         full_name = 'Guest User',        
#         password = generate_password_hash('guest'),
#         role = 'guest',
#         created_at = datetime.now(tz=ZoneInfo("UTC")) - timedelta(days=8),
#         is_verified = False
#     )
#     db.session.add(guest)
#     db.session.flush()
    
#     cart = Cart (
#         user_id = guest.id
#     )
#     db.session.add(cart)
#     db.session.flush()

#     return guest

@pytest.fixture
def test_admin_login(test_client, test_create_users):    
    response = test_client.post('/user/login', json={
        'email': 'admin@test.com',
        'password': 'password123',
        'remember_me': False
    })

    # Check if the response is valid
    assert response.status_code == 200

    # Extract cookies from the response headers
    cookies = response.headers.getlist('Set-Cookie')
    
    return cookies
    
@pytest.fixture
def test_logout(test_client):
    response = test_client.post('/user/logout')

    assert response.status_code == 200

    return response

# Category Fixtures
@pytest.fixture()
def create_test_category(test_client, test_admin_login):
    category_data = {
        'name': 'Test Category',
    }

    response = test_client.post('/category/admin', json=category_data)

    assert response.status_code == 201

    return response

# Address Fixtures
@pytest.fixture()
def create_test_address(test_client, test_customer_login):
    address_data = {
        'full_name': 'John Doe',
        'address_line_1': '123 Test Street',
        'address_line_2': 'Test Area',
        'city': 'Test City',
        'postcode': 'TE1 1ST',
        'is_default': True,
    }

    response = test_client.post('/address/', json=address_data)

    assert response.status_code == 201

    return response

# User Fixtures
@pytest.fixture()
def create_test_user(test_client, mocker):
    user_data = {        
        'full_name': 'John Doe',
        'email': 'testemail@test.com',
        'password': 'password123'
    }

    # Mock the send_email and generate_verification_token functions
    mocked_send_email = mocker.patch('services.user_service.send_email', return_value={'message': 'Email sent successfully'})
    mocked_generate_verification_token = mocker.patch('services.user_service.generate_verification_token', return_value='ImpvZWhhbGwwMjA3QGdtYWlsLmNvbSI.Z94M2g.j_sNmLt0NYzk5GwHuugjBBPWNQc')

    response = test_client.post('/user/signup', json=user_data)

    assert response.status_code == 201

    # Assert that the send_email function was called
    mocked_send_email.assert_called_once()
    mocked_generate_verification_token.assert_called_once()

    # return the response 
    return response

@pytest.fixture()
def create_unverified_user(db_session):
    user = User (
        full_name = 'John Doe',
        email = 'customer@test.com',
        password = generate_password_hash('password123'),
        role = 'customer',
        created_at = datetime.now(tz=ZoneInfo("UTC")),
        is_verified = False
    )
    db.session.add(user)
    db.session.flush()

@pytest.fixture()
def get_all_test_users(test_client, test_admin_login):
    response = test_client.get('/user/admin')

    assert response.status_code == 200
    
    return response

# Product Fixtures

@pytest.fixture()
def create_test_product(test_client, mocker, create_test_category, test_admin_login):
    product_data = {
        'name': 'Test Product',
        'description': 'Test Product Description',
        'price': 100.00,
        'stock': 10,
        'category_id': create_test_category.json['id']
    }

    # Mock the create_stripe_product_and_price function
    mocked_create_stripe_product_and_price = mocker.patch('services.product_service.create_stripe_product_and_price', return_value={'Stripe product created successfully'})

    response = test_client.post('/product/admin', json=product_data)

    assert response.status_code == 201

    # Assert that the create_stripe_product_and_price function was called
    mocked_create_stripe_product_and_price.assert_called_once()

    # Create a test image file
    test_image = io.BytesIO(b'Fake Image data')
    data = {
        'image': (test_image, 'test_image.jpg')
    }

    # Mock the upload_image_to_google_cloud_storage, remove_image_from_google_cloud_storage, upload_image_to_stripe_product function
    mocked_upload_image_to_google_cloud_storage = mocker.patch('services.product_service.upload_image_to_google_cloud_storage', return_value='test_image.jpg')
    mocked_upload_image_to_stripe_product = mocker.patch('services.product_service.upload_image_to_stripe_product', return_value={'message': 'Image uploaded successfully'})
    mocked_remove_image_from_google_cloud_storage = mocker.patch('services.product_service.remove_image_from_google_cloud_storage', return_value={'message': 'Image removed successfully'})

    imageResponse = test_client.post(f'/product/admin/product-image/{response.json['product_id']}', content_type='multipart/form-data', data=data)

    assert imageResponse.status_code == 201

    # Assert that the upload_image_to_google_cloud_storage, upload_image_to_stripe_product functions were called
    mocked_upload_image_to_google_cloud_storage.assert_called_once()
    mocked_upload_image_to_stripe_product.assert_called_once()

    return response, mocked_remove_image_from_google_cloud_storage

@pytest.fixture()
def create_four_test_products(test_client, mocker, create_test_category, test_admin_login):
    products = []

    for i in range(4):
        product_data = {
            'name': f'Test Product {i}',
            'description': f'Test Product Description {i}',
            'price': 100.00,
            'stock': 10,
            'category_id': create_test_category.json['id']
        }

        response = test_client.post('/product/admin', json=product_data)

        assert response.status_code == 201

        products.append(response)

        # Create a test image file
        test_image = io.BytesIO(b'Fake Image data')
        data = {
            'image': (test_image, f'test_image_{i}.jpg')
        }

        # Mock the upload_image_to_google_cloud_storage, remove_image_from_google_cloud_storage, upload_image_to_stripe_product function
        mocked_upload_image_to_google_cloud_storage = mocker.patch('services.product_service.upload_image_to_google_cloud_storage', return_value=f'test_image_{i}.jpg')
        mocked_upload_image_to_stripe_product = mocker.patch('services.product_service.upload_image_to_stripe_product', return_value={'message': 'Image uploaded successfully'})
        mocked_remove_image_from_google_cloud_storage = mocker.patch('services.product_service.remove_image_from_google_cloud_storage', return_value={'message': 'Image removed successfully'})

        imageResponse = test_client.post(f'/product/admin/product-image/{response.json['product_id']}', content_type='multipart/form-data', data=data)

        assert imageResponse.status_code == 201

        # Assert that the upload_image_to_google_cloud_storage, upload_image_to_stripe_product functions were called
        mocked_upload_image_to_google_cloud_storage.assert_called_once()
        mocked_upload_image_to_stripe_product.assert_called_once()

    return products, mocked_remove_image_from_google_cloud_storage

# Featured Product Fixtures
@pytest.fixture()
def create_test_featured_product(test_client, create_test_product, test_admin_login):
    product_id = create_test_product[0].json['product_id']

    response = test_client.post(f'/product/admin/featured-product/{product_id}')

    assert response.status_code == 201

    return response

@pytest.fixture()
def create_four_test_featured_products(test_client, create_four_test_products, test_admin_login):
    products = create_four_test_products[0]

    featured_products = []

    for product in products:
        product_id = product.json['product_id']

        response = test_client.post(f'/product/admin/featured-product/{product_id}')

        assert response.status_code == 201

        featured_products.append(response)

    return featured_products
  
# Cart Fixtures
@pytest.fixture()
def add_test_product_to_cart(test_client, create_test_product, test_admin_login):
    product_id = create_test_product[0].json['product_id']

    quantityData = {
        'quantity': 1
    }

    response = test_client.post(f'/cart/{product_id}', json=quantityData)

    assert response.status_code == 200

    return response

@pytest.fixture()
def get_all_test_products_in_cart(test_client, add_test_product_to_cart):
    response = test_client.get('/cart/')

    assert response.status_code == 200

    return response

# Order Fixtures
@pytest.fixture()
def create_test_order(test_client, mocker, add_test_product_to_cart, test_admin_login):
    order_data = {
        'user_id': get_jwt_identity(),
        'full_name': 'John Doe',
        'address_line_1': '123 Test Street',
        'address_line_2': 'Test Area',
        'city': 'Test City',
        'postcode': 'TE1 1ST',
        'customer_email': 'test@test.com'
    }
    
    # Mock the stripe_webhook_handler function
    mocked_stripe_webhook_handler = mocker.patch('api.order.stripe_webhook_handler', return_value=order_data)

    response = test_client.post('/order/webhook')

    assert response.status_code == 200

    return response