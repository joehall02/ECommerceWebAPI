from flask_testing import TestCase
from config import Test
from main import create_app
from exts import db
from werkzeug.http import parse_cookie

class BaseTestCase(TestCase):
    # Create an instance of the Flask app
    def create_app(self): 
        app = create_app(Test)
        return app

    # Set up the test client automatically before each test
    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()

        # Create the database and tables
        with self.app.app_context():
            db.drop_all()
            db.create_all()

        # Create a test user to be used accross all test cases
        response = self.client.post('user/signup', json={
            'full_name': 'Test_full_name',
            'email': 'Test_email@testemail.com',
            'password': 'Test_password123@!',            
            "role": "admin"
        })

        # Get the access token and refresh token
        response = self.client.post('user/login', json={
            'email': 'Test_email@testemail.com',
            'password': 'Test_password123@!'
        })

        # Parse the Set-Cookie headers to get the CSRF token
        cookies = response.headers.getlist('Set-Cookie')
        csrf_token = None
        for cookie in cookies:
            parsed_cookie = parse_cookie(cookie)
            if 'csrf_access_token' in parsed_cookie:
                csrf_token = parsed_cookie['csrf_access_token']
                break

        self.csrf_token = csrf_token     

        # Create a category
        self.client.post('/category/admin', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'name': 'Category_test'
        })

        # Create a product
        self.client.post('/product/admin', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'name': 'Product_test',
            'description': 'Product_description',
            'stock': 10,
            'price': 1000,
            'category_id': 1
        })

        # Create an address
        self.client.post('/address/', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'full_name': 'Test_full_name',
            'address_line_1': 'Test_address_line_1',
            'address_line_2': 'Test_address_line_2',
            'city': 'Test_city',
            'postcode': 'Test_postcode',
            'is_default': True
        })

        # Create a payment method
        self.client.post('/payment/', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'stripe_payment_id': 'Test_stripe_payment_id'
        })

    # Tear down the test client automatically after each test
    def tearDown(self):
        # Drop all tables
        with self.app.app_context():
            db.session.remove()
            db.drop_all()