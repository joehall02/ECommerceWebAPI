from base import BaseTestCase

# Tests for all category related endpoints
class CategoryTestCase(BaseTestCase):
    def setUp(self):
        super().setUp() # Call the setUp() method of the BaseTestCase class

        # Create a category
        self.client.post('/category/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Category_test'
        })

        # Create a category to be deleted
        self.client.post('/category/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Category_to_delete'
        })

        # Create a product
        self.client.post('/product/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Product_test',
            'description': 'Product_description',
            'stock': 10,
            'price': 1000,
            'category_id': 1
        })

    def test_create_category(self):
        # Send a POST request to the endpoint
        response = self.client.post('/category/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Test_category'
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 201)

    def test_get_categories(self):
        # Send a GET request to the endpoint
        response = self.client.get('/category/', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_get_products_in_category(self):
        # Send a GET request to the endpoint
        response = self.client.get('/category/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_update_category(self):
        # Send a PUT request to the endpoint
        response = self.client.put('/category/admin/1', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Updated_name'
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_delete_category(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/category/admin/2', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    