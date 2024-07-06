from flask_testing import TestCase
from config import Test
from main import create_app
from exts import db

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
            db.create_all()

        # Create a test user to be used accross all test cases
        response = self.client.post('user/signup', json={
            'first_name': 'Test_first_name',
            'last_name': 'Test_last_name',
            'email': 'Test_email@testemail.com',
            'password': 'Test_password123@!',
            'phone_number': '07853299124'
        })

        # Get the access token and refresh token
        response = self.client.post('user/login', json={
            'email': 'Test_email@testemail.com',
            'password': 'Test_password123@!'
        })

        data = response.get_json()

        # Set the access token and refresh token
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

    # Tear down the test client automatically after each test
    def tearDown(self):
        # Drop all tables
        with self.app.app_context():
            db.session.remove()
            db.drop_all()