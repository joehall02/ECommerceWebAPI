import pytest
from tests.utils import auth_customer_verification

# Fixtures
@pytest.fixture
def valid_cart_product_data():
    return {
        'quantity': 1,
    }

# Tests

# Test the get all products in the cart route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_all_products_in_cart(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)

    if (expected_status_code == 200):
        test_add_product_to_cart = request.getfixturevalue('add_test_product_to_cart')

    response = test_client.get('/cart/')

    assert response.status_code == expected_status_code

# Test the add product to cart route
@pytest.mark.parametrize('create_cart_product_data, expected_status_code', [
    ("valid_cart_product_data", 200), # Success Case
    ("missing_data", 400), # Failure Case: Missing Data
])

def test_add_product_to_cart(request, test_client, create_test_product, create_cart_product_data, expected_status_code):
    product_id = create_test_product[0].json['product_id']
    cart_product_data = request.getfixturevalue(create_cart_product_data)

    response = test_client.post(f'/cart/{product_id}', json=cart_product_data)

    assert response.status_code == expected_status_code

# Test the update product quantity in cart route
@pytest.mark.parametrize('update_cart_product_data, expected_status_code, auth_required', [
    ("valid_cart_product_data", 200, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing Data
    ("valid_cart_product_data", 401, False) # Unauthorised Case: User not logged in
])

def test_update_product_in_cart(request, test_client, get_all_test_products_in_cart, update_cart_product_data, expected_status_code, auth_required):
    cart_products = get_all_test_products_in_cart.json
    cart_product_id = cart_products[0]['cart_product']['id']
    cart_product_data = request.getfixturevalue(update_cart_product_data)

    auth_customer_verification(test_client, auth_required, request)

    response = test_client.put(f'/cart/{cart_product_id}', json=cart_product_data)

    assert response.status_code == expected_status_code

# Test the delete product from cart route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success case
    (401, False) # Unauthorised Case: User not logged in
])

def test_delete_product_in_cart(request, test_client, get_all_test_products_in_cart, expected_status_code, auth_required):
    cart_products = get_all_test_products_in_cart.json
    cart_product_id = cart_products[0]['cart_product']['id']

    auth_customer_verification(test_client, auth_required, request)

    response = test_client.delete(f'/cart/{cart_product_id}')

    assert response.status_code == expected_status_code