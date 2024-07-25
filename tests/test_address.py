from base import BaseTestCase

# Tests for all address related endpoints
class AddressTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    # Address tests
    def test_create_address(self):
        # Send a POST request to the endpoint
        response = self.client.post('/address/', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'address_line_1': 'Test_address_line_1',
            'address_line_2': 'Test_address_line_2',
            'city': 'Test_city',
            'postcode': 'Test_postcode'
        })

        self.assertEqual(response.status_code, 201)
    
    def test_get_addresses(self):
        # Send a GET request to the endpoint
        response = self.client.get('/address/', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
    
    def test_get_address(self):
        # Send a GET request to the endpoint
        response = self.client.get('/address/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
    
    def test_update_address(self):
        # Send a PUT request to the endpoint
        response = self.client.put('/address/1', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'address_line_1': 'Updated_address_line_1',
            'address_line_2': 'Updated_address_line_2',
            'city': 'Updated_city',
            'postcode': 'Updated_postcode'
        })

        self.assertEqual(response.status_code, 200)
    
    def test_delete_address(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/address/1', headers={'Authorization': 'Bearer ' + self.access_token})

        self.assertEqual(response.status_code, 200)