from base import BaseTestCase

# Tests for all category related endpoints
class CategoryTestCase(BaseTestCase):
    def setUp(self):
        super().setUp() # Call the setUp() method of the BaseTestCase class

        # Create a category to be deleted
        self.client.post('/category/admin', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'name': 'Category_to_delete'
        })

    def test_create_category(self):
        # Send a POST request to the endpoint
        response = self.client.post('/category/admin', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'name': 'Test_category'
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 201)

    def test_get_categories(self):
        # Send a GET request to the endpoint
        response = self.client.get('/category/', headers={
            'X-CSRF-TOKEN': self.csrf_token
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_get_products_in_category(self):
        # Send a GET request to the endpoint
        response = self.client.get('/category/1', headers={
            'X-CSRF-TOKEN': self.csrf_token
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_update_category(self):
        # Send a PUT request to the endpoint
        response = self.client.put('/category/admin/1', headers={
            'X-CSRF-TOKEN': self.csrf_token
        }, json={
            'name': 'Updated_name'
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_delete_category(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/category/admin/2', headers={
            'X-CSRF-TOKEN': self.csrf_token
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    