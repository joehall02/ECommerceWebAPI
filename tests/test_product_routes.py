import io
import pytest
from tests.utils import auth_admin_verification, auth_customer_verification

# Fixtures

@pytest.fixture
def valid_product_data(create_test_category):
    return {
        'name': 'Test Product',
        'description': 'Test Description',
        'price': 10.00,
        'stock': 10,
        'category_id': create_test_category.json['id']
    }

@pytest.fixture
def valid_update_product_data():
    return {
        'name': 'Updated Product',
        'description': 'Updated Description',
        'price': 20.00,
        'stock': 20        
    }

# Product Test Cases

# Test the get all products route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, False), # Success Case
])

def test_get_all_products(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    if (expected_status_code == 200):
        test_create_product = request.getfixturevalue('create_test_product') # Create a product and upload a product image

    response = test_client.get('/product/')

    assert response.status_code == expected_status_code

# Test the get product by id route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, False), # Success Case
    (400, False) # Failure Case: Invalid Product ID
])

def test_get_product(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    product_id = 1

    if (expected_status_code == 200):
        test_create_product = request.getfixturevalue('create_test_product')

        product_id = test_create_product[0].json['product_id']
    
    response = test_client.get(f'/product/{product_id}')

    assert response.status_code == expected_status_code

# Test the create product route (Admin)
@pytest.mark.parametrize('create_product_data, expected_status_code, auth_required', [
    ("valid_product_data", 201, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing Data
    ("valid_product_data", 401, False), # Unauthorised Case: User not logged in
    ('valid_product_data', 403, True) # Failure Case: User not an admin
])

def test_create_product(request, test_client, mocker, create_product_data, expected_status_code, auth_required):
    product_data = request.getfixturevalue(create_product_data)

    if (expected_status_code != 403):
        # Set/unset the authentication cookies
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set the authentication cookies for a non-admin user
        auth_customer_verification(test_client, auth_required, request)
    
    # Mock the create_stripe_product_and_price function
    mocked_create_stripe_product_and_price = mocker.patch('services.product_service.create_stripe_product_and_price', return_value={'message': 'Product created successfully'})

    response = test_client.post('/product/admin', json=product_data)

    assert response.status_code == expected_status_code

    if (expected_status_code == 201):
        # Assert that the create_stripe_product_and_price function was called
        mocked_create_stripe_product_and_price.assert_called_once()

# Test the update product route (Admin)
@pytest.mark.parametrize('update_product_data, expected_status_code, auth_required', [
    ("valid_update_product_data", 200, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing Data
    ("valid_update_product_data", 401, False), # Unauthorised Case: User not logged in
    ('valid_update_product_data', 403, True) # Failure Case: User not an admin
])

def test_update_product(request, test_client, mocker, create_test_product, update_product_data, expected_status_code, auth_required):
    product_data = request.getfixturevalue(update_product_data)

    product_id = create_test_product[0].json['product_id']

    if (expected_status_code != 403):
        # Set/unset the authentication cookies
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set the authentication cookies for a non-admin user
        auth_customer_verification(test_client, auth_required, request)
    
    # Mock the update_stripe_product function
    mocked_update_stripe_product_and_price = mocker.patch('services.product_service.update_stripe_product_and_price', return_value={'message': 'Product updated successfully'})

    response = test_client.put(f'/product/admin/{product_id}', json=product_data)

    assert response.status_code == expected_status_code

    if (expected_status_code == 200):
        # Assert that the update_stripe_product function was called
        mocked_update_stripe_product_and_price.assert_called_once()

# Test the delete product route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Invalid Product ID
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Failure Case: User not an admin
])

def test_delete_product(request, test_client, mocker, expected_status_code, auth_required):
    if (expected_status_code != 403):
        # Set/unset the authentication cookies
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set the authentication cookies for a non-admin user
        auth_customer_verification(test_client, auth_required, request)

    product_id = 1

    if (expected_status_code == 200):
        test_create_product, mocked_remove_image_from_google_cloud_storage = request.getfixturevalue('create_test_product')

        product_id = test_create_product.json['product_id']

    response = test_client.delete(f'/product/admin/{product_id}')

    assert response.status_code == expected_status_code

    if (expected_status_code == 200):
        # Assert that the delete_stripe_product function was called
        mocked_remove_image_from_google_cloud_storage.assert_called_once()

# Test get all admin products route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Failure Case: User not an admin
])

def test_get_all_admin_products(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set the authentication cookies for a non-admin user
        auth_customer_verification(test_client, auth_required, request)

    if (expected_status_code == 200):
        test_create_product = request.getfixturevalue('create_test_product')

    response = test_client.get('/product/admin')

    assert response.status_code == expected_status_code

# Featured Product Test Cases

# Test the get featured products route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, False), # Success Case
    (400, False) # Failure Case: No Featured Products
])

def test_get_featured_products(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)

    if (expected_status_code == 200):
        test_create_featured_product = request.getfixturevalue('create_test_featured_product')

    response = test_client.get('/product/featured-product')

    assert response.status_code == expected_status_code

# Test the add featured product route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (201, True), # Success Case
    (400, True), # Failure Case: Already 4 Featured Products
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Failure Case: User not an admin
])

def test_add_featured_product(request, test_client, create_test_product, expected_status_code, auth_required):
    product_id = create_test_product[0].json['product_id']
   
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    if (expected_status_code == 400):
        test_create_four_featured_products = request.getfixturevalue('create_four_test_featured_products')

    response = test_client.post(f'/product/admin/featured-product/{product_id}')

    assert response.status_code == expected_status_code

# Test the delete featured product route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Invalid Featured Product ID
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Failure Case: User not an admin
])

def test_delete_featured_product(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    featured_product_id = 1

    if (expected_status_code == 200):
        test_create_featured_product = request.getfixturevalue('create_test_featured_product')

        featured_product_id = test_create_featured_product.json['id']

    response = test_client.delete(f'/product/admin/featured-product/{featured_product_id}')

    assert response.status_code == expected_status_code

# Test the check featured product route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Invalid Product ID
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Failure Case: User not an admin
])

def test_check_featured_product(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    product_id = 1

    if (expected_status_code == 200):
        test_create_featured_product = request.getfixturevalue('create_test_featured_product')

        product_id = test_create_featured_product.json['product_id']

    response = test_client.get(f'/product/admin/featured-product/{product_id}')

    assert response.status_code == expected_status_code

# Product Image Test Cases


# Test the get product image route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, False),
    (400, False)
])

def test_get_product_image(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)

    product_id = 1

    if (expected_status_code == 200):
        test_create_product = request.getfixturevalue('create_test_product')

        product_id = test_create_product[0].json['product_id']

    response = test_client.get(f'/product/product-image/{product_id}')

# Test the upload product image route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (201, True), # Success Case
    (400, True), # Failure Case: No Image Provided
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Failure Case: User not an admin
])

def test_upload_product_image(request, test_client, create_test_product, expected_status_code, auth_required):
    product_id = create_test_product[0].json['product_id']

    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    data = None

    if (expected_status_code == 201):
        # Create a new BytesIO object for the image data
        test_create_image = io.BytesIO(b'Fake Image data')

        data = {
            'image': (test_create_image, 'test_image.jpg')
        }

    response = test_client.post(f'/product/admin/product-image/{product_id}', data=data)

    assert response.status_code == expected_status_code

    assert response.status_code == expected_status_code