from flask_jwt_extended import get_jwt_identity
import pytest
from pytest_mock import mocker
from tests.utils import auth_admin_verification, auth_customer_verification

# Fixtures

# Mock class for stripe checkout session
class MockStripeCheckoutSession:
    def __init__(self, id):
        self.id = id

@pytest.fixture
def valid_create_checkout_session_data():
    return {
        'full_name': 'John Doe',
        'address_line_1': '123 Test Street',
        'city': 'Test City',
        'postcode': 'TE1 1ST',
    }

@pytest.fixture
def valid_order_data():
    return {
        'user_id': get_jwt_identity(),
        'full_name': 'John Doe',
        'address_line_1': '123 Test Street',
        'address_line_2': 'Test Area',
        'city': 'Test City',
        'postcode': 'TE1 1ST',
        'customer_email': 'test@test.com',
        'stripe_session_id': 'test_session_id',
    }

@pytest.fixture
def valid_update_order_data():
    return {
        'status': 'Shipped',
        'tracking_url': 'http://tracking.url/12345',
    }

# Test cases

# Test the get all orders route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_all_orders(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)
    
    if (expected_status_code == 200):
        test_create_order = request.getfixturevalue('create_test_order')

    response = test_client.get('/order/')

    assert response.status_code == expected_status_code

# Test the get stripe checkout session route
@pytest.mark.parametrize('create_order_data, expected_status_code, auth_required', [
    ("valid_create_checkout_session_data", 200, True), # Success Case
    ("missing_data", 400, True) # Failure Case: Missing Data
])

def test_get_stripe_checkout_session(request, test_client, add_test_product_to_cart, mocker, create_order_data, expected_status_code, auth_required):
    order_data = request.getfixturevalue(create_order_data)

    auth_admin_verification(test_client, auth_required, request)

    mocked_create_stripe_checkout_session = mocker.patch('services.order_service.create_stripe_checkout_session', return_value=MockStripeCheckoutSession('test_session_id'))

    response = test_client.post('/order/checkout', json=order_data)

    assert response.status_code == expected_status_code

    if (expected_status_code == 200):
        mocked_create_stripe_checkout_session.assert_called_once()

# Test create order route
@pytest.mark.parametrize('create_order_data, expected_status_code, auth_required', [
    ("valid_order_data", 200, True), # Success Case
    # ("missing_data", 400, True) # Failure Case: Missing Data
])

def test_create_order(request, test_client, mocker, add_test_product_to_cart, create_order_data, expected_status_code, auth_required):
    order_data = request.getfixturevalue(create_order_data)

    auth_customer_verification(test_client, auth_required, request)

    mocked_stripe_webhook_handler = mocker.patch('api.order.stripe_webhook_handler', return_value=order_data)

    response = test_client.post('/order/webhook')

    assert response.status_code == expected_status_code

    if (expected_status_code == 200):
        mocked_stripe_webhook_handler.assert_called_once()
        
# Test the get all customer orders route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_all_customer_orders(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)
    
    if (expected_status_code == 200):
        test_create_order = request.getfixturevalue('create_test_order')

    response = test_client.get('/order/admin')

    assert response.status_code == expected_status_code

# Test the get order route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_order(request, test_client, create_test_order, expected_status_code, auth_required):
    order_id = create_test_order.json['id']

    auth_admin_verification(test_client, auth_required, request)

    response = test_client.get(f'/order/admin/{order_id}')

    assert response.status_code == expected_status_code

# Test the update order route (Admin)
@pytest.mark.parametrize('update_order_data, expected_status_code, auth_required', [
    ("valid_update_order_data", 200, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing data
    ("valid_update_order_data", 401, False) # Unauthorised Case: User not logged in
])

def test_update_order(request, test_client, mocker, create_test_order, update_order_data, expected_status_code, auth_required):
    order_id = create_test_order.json['id']

    order_data = request.getfixturevalue(update_order_data)

    auth_admin_verification(test_client, auth_required, request)

    mocked_send_email = mocker.patch('services.order_service.send_email', return_value={'message': 'Email sent successfully'})

    response = test_client.put(f'/order/admin/{order_id}', json=order_data)

    assert response.status_code == expected_status_code

    if (expected_status_code == 200):
        mocked_send_email.assert_called_once()

# Test the get all orders for a user route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True),
    (401, False)
])

def test_get_all_orders_for_user(request, test_client, get_all_test_users, expected_status_code, auth_required):
    users = get_all_test_users.json['users']
    user_id = users[0]['id']

    auth_admin_verification(test_client, auth_required, request)

    response = test_client.get(f'/order/admin/user/{user_id}')

    assert response.status_code == expected_status_code

# Test check stripe session status route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Order not found
    (401, False) # Unauthorised Case: User not logged in
])

def test_check_stripe_session_status(request, test_client, expected_status_code, auth_required):
    if (expected_status_code == 200):
        test_create_order = request.getfixturevalue('create_test_order')

    auth_customer_verification(test_client, auth_required, request)

    response = test_client.get(f'/order/stripe_session_status?session_id=test_session_id')

    assert response.status_code == expected_status_code