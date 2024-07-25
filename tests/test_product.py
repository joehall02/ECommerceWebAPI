from base import BaseTestCase

# Tests for all product related endpoints
class ProductTestCase(BaseTestCase):
    def setUp(self):
        super().setUp() # Call the setUp() method of the BaseTestCase class

        # Create a product to be deleted
        self.client.post('/product/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Product_to_delete',
            'description': 'Product_description',
            'stock': 10,
            'price': 1000,
            'category_id': 1
        })

        # Create a featured product
        self.client.post('/product/admin/featured-product/1', headers={'Authorization': 'Bearer ' + self.access_token})

    # Product tests
    def test_create_product(self):
        # Send a POST request to the endpoint
        response = self.client.post('/product/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Test_product',
            'description': 'Test_description',
            'stock': 10,
            'price': 1000,
            'category_id': 1
        })

        self.assertEqual(response.status_code, 201)

    def test_get_products(self):
        # Send a GET request to the endpoint
        response = self.client.get('/product/', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_get_product(self):
        # Send a GET request to the endpoint
        response = self.client.get('/product/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_update_product(self):
        # Send a PUT request to the endpoint
        response = self.client.put('/product/admin/1', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Updated_name',
            'description': 'Updated_description',
            'stock': 10,
            'price': 1000,
            'category_id': 1
        })

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_delete_product(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/product/admin/2', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)


    # Featured product tests
    def test_get_featured_products(self):
        # Send a GET request to the endpoint
        response = self.client.get('/product/featured-product', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_create_featured_product(self):
        # Send a POST request to the endpoint
        response = self.client.post('/product/admin/featured-product/2', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 201)

    def test_get_featured_product(self):
        # Send a GET request to the endpoint
        response = self.client.get('/product/featured-product/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_delete_featured_product(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/product/admin/featured-product/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
