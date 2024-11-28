from base import BaseTestCase

# Tests for all user related endpoints
class UserTestCase(BaseTestCase):
    def setUp(self):
        super().setUp() # Call the setUp() method of the BaseTestCase class

    def test_signup(self):    
        # Send a POST request to the endpoint
        response = self.client.post('/user/signup', json={
            'full_name': 'Test_full_name2',
            'email': 'Test_email2@testemail.com',
            'password': 'Test_password123@!'            
        })         

        # Check if the response is correct
        self.assertEqual(response.status_code, 201)
        
    def test_login(self):
        # Create a new user account
        response = self.client.post('/user/login', json={
            'email': 'Test_email@testemail.com',
            'password': 'Test_password123@!'
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        # Reset the user password
        response = self.client.put('/user/reset-password', json={
            'email': 'Test_email@testemail.com',
            'password': 'Test_password1234@!',
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
        
    def test_refresh(self): 
        # Create a new access token
        response = self.client.post('/user/refresh', headers={'Authorization': 'Bearer ' + self.refresh_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)