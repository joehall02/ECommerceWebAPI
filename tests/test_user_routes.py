import pytest
from pytest_mock import mocker
from tests.utils import auth_customer_verification, auth_admin_verification
from models import User
from datetime import datetime
from werkzeug.security import generate_password_hash
from exts import db

# Fixtures

@pytest.fixture()
def valid_user_data():
    return {
        'full_name': 'John Doe',
        'email': 'testemail@test.com',
        'password': 'password123'
    }

@pytest.fixture()
def invalid_user_data():
    return {
        'full_name': 'John Doe',
        'password': 'password'
    }

@pytest.fixture()
def valid_token_data():
    return 'ImpvZWhhbGwwMjA3QGdtYWlsLmNvbSI.Z94M2g.j_sNmLt0NYzk5GwHuugjBBPWNQc'

@pytest.fixture()
def invalid_token_data():
    return 'invalid_token'

@pytest.fixture()
def valid_resend_verification_data():
    return {
        'email': 'customer@test.com'
    }

@pytest.fixture()
def valid_send_password_reset_email_data():
    return {
        'email': 'customer@test.com'
    }

@pytest.fixture()
def valid_reset_password_data():
    return {
        'new_password': 'new_password123'
    }

@pytest.fixture()
def invalid_reset_password_data():
    return {
        'new_password': '123'
    }

@pytest.fixture()
def valid_login_data():
    return {
        'email': 'customer@test.com',
        'password': 'password123',
        'remember_me': False
    }

@pytest.fixture()
def invalid_login_data():
    return {
        'email': 'customer@test.com',
        'password': 'password',
        'remember_me': False
    }

@pytest.fixture()
def valid_contact_us_data():
    return {
        'from_name': 'John Doe',
        'from_email': 'test@test.com',
        'subject': 'Test Subject',
        'message': 'Test Message'
    }

@pytest.fixture()
def valid_edit_name_data():
    return {
        'full_name': 'Jane Doe'
    }

@pytest.fixture()
def valid_edit_password_data():
    return {
        'current_password': 'password123',
        'new_password': 'new_password123'
    }

@pytest.fixture()
def invalid_edit_password_data():
    return {
        'current_password': 'password',
        'new_password': '123'
    }

# Test Cases

# Test the create user route
@pytest.mark.parametrize('user_data, expected_status_code', [
    ("valid_user_data", 201), # Success Case
    ("invalid_user_data", 400), # Failure Case: Invalid Data
    ("missing_data", 400) # Failure Case: Missing Data
])

def test_create_user(request, test_client, mocker, user_data, expected_status_code):
    user = request.getfixturevalue(user_data)
    
    # Mock the send_email function
    mocked_send_email = mocker.patch('services.user_service.send_email', return_value={'message': 'Email sent successfully'})
    mocked_generate_verification_token = mocker.patch('services.user_service.generate_verification_token', return_value='verification_token')

    response = test_client.post('/user/signup', json=user)

    assert response.status_code == expected_status_code

    # Assert that the send_email function was called
    if expected_status_code == 201:
        mocked_send_email.assert_called_once()
        mocked_generate_verification_token.assert_called_once()

# Test the verify email route
@pytest.mark.parametrize('token_data, expected_status_code', [
    ("valid_token_data", 200), # Success Case
    ("invalid_token_data", 400), # Failure Case: Invalid Token
    ("missing_data", 400) # Failure Case: Missing Data
])

def test_verify_email(request, mocker, test_client, create_test_user, token_data, expected_status_code):
    token = request.getfixturevalue(token_data)

    # Mock the verify_token function
    mocked_verify_token = mocker.patch('services.user_service.verify_token', return_value='testemail@test.com')

    response = test_client.post(f'/user/verify-email/{token}')

    assert response.status_code == expected_status_code

    # Assert that the verify_token function was called
    if expected_status_code == 200:
        mocked_verify_token.assert_called_once()

# Test the resend verification email route
@pytest.mark.parametrize('email_data, expected_status_code', [
    ("valid_resend_verification_data", 200), # Success Case
    ("missing_data", 400) # Failure Case: Missing Data
])

# Uses create_unverified_user instead of create_test_user to avoid please wait before sending another email error
def test_resend_verification_email(request, mocker, test_client, create_unverified_user, email_data, expected_status_code): 
    email = request.getfixturevalue(email_data)

    # Mock the send_email and generate_verification_token functions
    mocked_generate_verification_token = mocker.patch('services.user_service.generate_verification_token', return_value='verification_token')
    mocked_send_email = mocker.patch('services.user_service.send_email', return_value={'message': 'Email sent successfully'})

    response = test_client.post('/user/resend-verification', json=email)

    print(response.json)

    assert response.status_code == expected_status_code

    # Assert that the send_email function was called
    if expected_status_code == 200:
        mocked_generate_verification_token.assert_called_once()
        mocked_send_email.assert_called_once()

# Test send password reset email route
@pytest.mark.parametrize('email_data, expected_status_code', [
    ("valid_send_password_reset_email_data", 200), # Success Case
    ("missing_data", 400) # Failure Case: Missing Data
])

def test_send_password_reset_email(request, mocker, test_client, test_create_users, email_data, expected_status_code):
    email = request.getfixturevalue(email_data)

    # Mock the send_email and generate_verification_token functions
    mocked_generate_verification_token = mocker.patch('services.user_service.generate_verification_token', return_value='verification_token')
    mocked_send_email = mocker.patch('services.user_service.send_email', return_value={'message': 'Email sent successfully'})

    response = test_client.post('/user/reset-password', json=email)

    assert response.status_code == expected_status_code

    # Assert that the send_email function was called
    if expected_status_code == 200:
        mocked_generate_verification_token.assert_called_once()
        mocked_send_email.assert_called_once()
    
# Test the reset password route
@pytest.mark.parametrize('token_data, reset_password_data, expected_status_code', [
    ("valid_token_data", "valid_reset_password_data", 200), # Success Case
    ("invalid_token_data", "valid_reset_password_data", 400), # Failure Case: Invalid Token
    ("valid_token_data", "invalid_reset_password_data", 400), # Failure Case: Invalid Data
    ("valid_token_data", "missing_data", 400) # Failure Case: Missing Data
])

def test_reset_password(request, mocker, test_client, create_test_user, token_data, reset_password_data, expected_status_code):
    token = request.getfixturevalue(token_data)
    reset_password = request.getfixturevalue(reset_password_data)

    # Mock the verify_token function
    mocked_verify_token = mocker.patch('services.user_service.verify_token', return_value='testemail@test.com')

    response = test_client.put(f'/user/reset-password/{token}', json=reset_password)

    print(response.json)

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        mocked_verify_token.assert_called_once()

# Test login user route
@pytest.mark.parametrize('user_data, expected_status_code', [
    ("valid_login_data", 200), # Success Case
    ("invalid_login_data", 400), # Failure Case: Invalid Data
    ("missing_data", 400) # Failure Case: Missing Data
])

def test_login_user(request, test_client, test_create_users, user_data, expected_status_code):
    user = request.getfixturevalue(user_data)

    response = test_client.post('/user/login', json=user)

    assert response.status_code == expected_status_code
    
# Test the authenticate user route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_authenticate_user(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.get('/user/authenticate')

    assert response.status_code == expected_status_code

# Test refresh token route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_refresh_token(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.post('/user/refresh')

    assert response.status_code == expected_status_code

# Test logout user route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_logout_user(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.post('/user/logout')

    print(response.json)

    assert response.status_code == expected_status_code

# Test the contact us route
@pytest.mark.parametrize('email_data, expected_status_code', [
    ("valid_contact_us_data", 200), # Success Case
    ("missing_data", 400), # Failure Case: Missing Data
    # ("valid_contact_us_data", 429) # Failure Case: Rate Limit Exceeded
])

def test_contact_us(request, test_client, mocker, email_data, expected_status_code):
    email = request.getfixturevalue(email_data)

    # Mock the send_contact_us_email function
    mocked_send_contact_us_email = mocker.patch('services.user_service.send_contact_us_email', return_value={'message': 'Email sent successfully'})

    response = test_client.post('/user/contact-us', json=email)

    assert response.status_code == expected_status_code

    # Assert that the send_contact_us_email function was called
    if expected_status_code == 200:
        mocked_send_contact_us_email.assert_called_once()


# Test the edit name route
@pytest.mark.parametrize('name_data, expected_status_code, auth_required', [
    ("valid_edit_name_data", 200, True), # Success Case
    ("missing_data", 400, True), # Failure Case: Missing Data
    ("valid_edit_name_data", 401, False) # Unauthorised Case: User not logged in
])

def test_edit_name(request, test_client, name_data, expected_status_code, auth_required):
    name = request.getfixturevalue(name_data)

    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.put('/user/edit-name', json=name)

    assert response.status_code == expected_status_code

# Test the edit password route
@pytest.mark.parametrize('password_data, expected_status_code, auth_required', [
    ("valid_edit_password_data", 200, True), # Success Case
    ("invalid_edit_password_data", 400, True), # Failure Case
    ("missing_data", 400, True), # Failure Case: Missing Data
    ("valid_edit_password_data", 401, False) # Unauthorised Case: User not logged in
])

def test_edit_password(request, test_client, password_data, expected_status_code, auth_required):
    password = request.getfixturevalue(password_data)

    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.put('/user/edit-password', json=password)

    assert response.status_code == expected_status_code

# Test delete user route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_delete_user(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.delete('/user/delete-account')

    assert response.status_code == expected_status_code

# Test get full name route
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False) # Unauthorised Case: User not logged in
])

def test_get_full_name(request, test_client, expected_status_code, auth_required):
    # Set/unset the authentication cookies
    auth_customer_verification(test_client, auth_required, request)

    response = test_client.get('/user/')

    assert response.status_code == expected_status_code

# Test get all admin users route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Forbidden Case: User not an admin
])

def test_get_all_admin_users(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        # Set/unset the authentication cookies
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set/unset the authentication cookies
        auth_customer_verification(test_client, auth_required, request)

    response = test_client.get('/user/admin')

    assert response.status_code == expected_status_code

# Test get a user route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True), # Success Case
    (400, True), # Failure Case: User Not Found
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Forbidden Case: User not an admin
])

def test_get_user(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        # Set/unset the authentication cookies
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set/unset the authentication cookies
        auth_customer_verification(test_client, auth_required, request)

    user_id = 1

    if (expected_status_code == 200):
        create_test_user = request.getfixturevalue('create_test_user')
        user_id = create_test_user.json['id']

    response = test_client.get(f'/user/admin/{user_id}')

    assert response.status_code == expected_status_code

# Test get dashboard data route (Admin)
@pytest.mark.parametrize('expected_status_code, auth_required', [
    (200, True),
    (401, False), # Unauthorised Case: User not logged in
    (403, True) # Forbidden Case: User not an admin
])

def test_get_dashboard_data(request, test_client, expected_status_code, auth_required):
    if (expected_status_code != 403):
        # Set/unset the authentication cookies
        auth_admin_verification(test_client, auth_required, request)
    else:
        # Set/unset the authentication cookies
        auth_customer_verification(test_client, auth_required, request)

    response = test_client.get('/user/admin/dashboard')

    assert response.status_code == expected_status_code