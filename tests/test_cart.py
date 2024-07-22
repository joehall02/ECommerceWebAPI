from base import BaseTestCase

# Tests for all cart related endpoints
class CartTestCase(BaseTestCase):
    def setUp(self):
        super().setUp() # Call the setUp() method of the BaseTestCase class

        # Create a user
        self.client.post('/user/signup', json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@gmail.com',
            'password': 'Password123@!',
            'phone_number': '07853299124'
        })

        # Login the user
        self.client.post('/user/login', json={
            'email': 'johndoe@gmail.com',
            'password': 'Password123@!',
        })

        # Create a category
        self.client.post('/category/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Category_test'
        })

        # Create a product
        self.client.post('/product/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Product_test',
            'description': 'Product_description',
            'stock': 10,
            'price': 1000,
            'category_id': 1
        })

        # Create another product
        self.client.post('/product/admin', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'name': 'Product_test2',
            'description': 'Product_description2',
            'stock': 5,
            'price': 500,
            'category_id': 1
        })

        # Add the product to the cart
        self.client.post('/cart/1', headers={'Authorization': 'Bearer ' + self.access_token})

    def test_add_product_to_cart(self):
        # Send a POST request to the endpoint
        response = self.client.post('/cart/2', headers={'Authorization': 'Bearer ' + self.access_token})

        print(response.json)

        # Check if the response is correct
        self.assertEqual(response.status_code, 201)

    def test_get_all_products_in_cart(self):
        # Send a GET request to the endpoint
        response = self.client.get('/cart/', headers={'Authorization': 'Bearer ' + self.access_token})

        print(response.json)

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_delete_product_from_cart(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/cart/1', headers={'Authorization': 'Bearer ' + self.access_token})

        print(response.json)

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
        
            
            
            