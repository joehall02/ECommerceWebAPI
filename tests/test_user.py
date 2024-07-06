from base import BaseTestCase

# Tests for all user related endpoints
class UserTestCase(BaseTestCase):
    def test_signup(self):    
        # Send a POST request to the endpoint
        response = self.client.post('/user/signup', json={
            'first_name': 'Test_first_name',
            'last_name': 'Test_last_name',
            'email': 'Test_email2@testemail.com',
            'password': 'Test_password123@!',
            'phone_number': '07853859124'
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
        
    def test_refresh(self): 
        # Create a new access token
        response = self.client.post('/user/refresh', headers={'Authorization': 'Bearer ' + self.refresh_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)