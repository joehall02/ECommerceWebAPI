import pytest
from tests.utils import set_auth_cookies, auth_customer_verification

# Fixtures
@pytest.fixture
def valid_address_data():
    return {
        'full_name': 'John Doe',
        'address_line_1': '123 Test Street',
        'address_line_2': 'Test Area',
        'city': 'Test City',
        'postcode': 'TE1 1ST',
        'is_default': True,
    }

@pytest.fixture
def invalid_address_data():
    return {
        'full_name': 'John Doe',      
        'address_line_2': 'Test Area',
        'city': 'Test City',
        'postcode': 'TE1 1ST',
        'is_default': True,
    }

@pytest.fixture
def valid_update_address_data():
    return {
        'city': 'Updated City',
        'is_default': False
    }

# Test Cases

# Test the create address route
@pytest.mark.parametrize('create_address_data, expected_status_code, auth_required', [
    ("valid_address_data", 201, True), # Success Case
    ("invalid_address_data", 400, True), # Failure Case: Invalid Data
    ("valid_address_data", 401, False) # Unauthorised Case: User not logged in
])

def test_create_address(request, test_client, create_address_data, expected_status_code, auth_required):
    address_data = request.getfixturevalue(create_address_data)

    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    response = test_client.post('/address/', json=address_data)

    assert response.status_code == expected_status_code

# Test the update address route
@pytest.mark.parametrize('update_address_data, expected_status_code, auth_required', [
    ("valid_update_address_data", 200, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing data
    ("valid_update_address_data", 401, False) # Unauthorised Case: User not logged in
])

def test_update_address(request, test_client, create_test_address, update_address_data, expected_status_code, auth_required):
    address_data = request.getfixturevalue(update_address_data)

    address_id = create_test_address.json['id']

    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    response = test_client.put(f'/address/{address_id}', json=address_data)

    assert response.status_code == expected_status_code

# Test the get all addresses route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: No Addresses Found
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_all_addresses(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    # Create a test address only if the expected status code is 200
    if (expected_status_code == 200):
        test_create_address = request.getfixturevalue('create_test_address')

    response = test_client.get('/address/')

    assert response.status_code == expected_status_code

# Test the get default address route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: No Default Address Found
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_default_address(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    # Create a test address only if the expected status code is 200
    if (expected_status_code == 200):
        test_create_address = request.getfixturevalue('create_test_address')

    response = test_client.get('/address/default')

    assert response.status_code == expected_status_code

# Test the get single address route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Address Not Found
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_address(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    address_id = 1

    # Create a test address only if the expected status code is 200
    if (expected_status_code == 200):
        test_create_address = request.getfixturevalue('create_test_address')

        address_id = test_create_address.json['id']

    response = test_client.get(f'/address/{address_id}')

    assert response.status_code == expected_status_code

# Test the delete address route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Address Not Found
    (401, False) # Unauthorised Case: User not logged in
])

def test_delete_address(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)
    
    address_id = 1

    # Create a test address only if the expected status code is 200
    if (expected_status_code == 200):
        test_create_address = request.getfixturevalue('create_test_address')

        address_id = test_create_address.json['id']

    response = test_client.delete(f'/address/{address_id}')

    assert response.status_code == expected_status_code