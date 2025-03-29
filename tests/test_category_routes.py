import pytest
from tests.utils import auth_admin_verification, auth_customer_verification

# Fixtures

@pytest.fixture
def valid_category_data():
    return {
        'name': 'Test Category',
    }

@pytest.fixture
def valid_update_category_data():
    return {
        'name': 'Updated Category',
    }

# Test cases

# Test the get all categories route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, False), # Success Case
    (400, False) # Failure Case: No Categories Found
])

def test_get_all_categories(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)
    
    if (expected_status_code == 200):
        test_create_category = request.getfixturevalue('create_test_category')

    response = test_client.get('/category/')

    assert response.status_code == expected_status_code

# Test the get category details route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, False), # Success Case
    (400, False) # Failure Case: Invalid Category ID
])

def test_get_category(request, test_client, expected_status_code, auth_required):
    auth_customer_verification(test_client, auth_required, request)
    
    category_id = 1

    if (expected_status_code == 200):
        create_category = request.getfixturevalue('create_test_category')

        category_id = create_category.json['id']

    response = test_client.get(f'/category/{category_id}')

    assert response.status_code == expected_status_code

# Test the create category route (Admin)
@pytest.mark.parametrize('create_category_data, expected_status_code, auth_required', [
    ("valid_category_data", 201, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Invalid Data
    ("valid_category_data", 401, False), # Unauthorised Case: User not logged in
    ("valid_category_data", 403, True) # Forbidden Case: User not an admin
])

def test_create_category(request, test_client, create_category_data, expected_status_code, auth_required):
    category_data = request.getfixturevalue(create_category_data)
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    response = test_client.post('/category/admin', json=category_data)

    assert response.status_code == expected_status_code

# Test get all categories route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: No Categories Found
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Forbidden Case: User not an admin
])

def test_get_all_categories_admin(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    if (expected_status_code == 200):
        test_create_category = request.getfixturevalue('create_test_category')

    response = test_client.get('/category/admin')

    assert response.status_code == expected_status_code

# Test the update category route (Admin)
@pytest.mark.parametrize('update_category_data, expected_status_code, auth_required', [
    ("valid_update_category_data", 200, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing data
    ("valid_update_category_data", 401, False), # Unauthorised Case: User not logged in
    ("valid_update_category_data", 403, True) # Forbidden Case: User not an admin
])

def test_update_category(request, test_client, create_test_category, update_category_data, expected_status_code, auth_required):
    category_data = request.getfixturevalue(update_category_data)

    category_id = create_test_category.json['id']

    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    response = test_client.put(f'/category/admin/{category_id}', json=category_data)

    assert response.status_code == expected_status_code

# Test the delete category route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: Invalid Category ID
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Forbidden Case: User not an admin
])

def test_delete_category(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        auth_admin_verification(test_client, auth_required, request)
    else:
        auth_customer_verification(test_client, auth_required, request)

    category_id = 1

    if (expected_status_code == 200):
        create_category = request.getfixturevalue('create_test_category')

        category_id = create_category.json['id']

    response = test_client.delete(f'/category/admin/{category_id}')

    assert response.status_code == expected_status_code
