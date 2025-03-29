from sqlalchemy import text

# Set the authentication cookies
def set_auth_cookies(client, cookies):
    for cookie in cookies:
        client.set_cookie('localhost', cookie)

# Set and unset the authentication cookies based on the auth_required parameter for the customer
def auth_customer_verification(test_client, auth_required, request):
    test_customer_login = request.getfixturevalue('test_customer_login')
    set_auth_cookies(test_client, test_customer_login)
    
    # If auth required is false, unset the authentication cookies
    if not auth_required:
        # Unset the authetication cookies
        test_logout = request.getfixturevalue('test_logout')

# Set and unset the authentication cookies based on the auth_required parameter for the admin
def auth_admin_verification(test_client, auth_required, request):
    test_admin_login = request.getfixturevalue('test_admin_login')
    set_auth_cookies(test_client, test_admin_login)
    
    # If auth required is false, unset the authentication cookies
    if not auth_required:
        # Unset the authetication cookies
        test_logout = request.getfixturevalue('test_logout')