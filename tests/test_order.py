from base import BaseTestCase

# Test all order related endpoints

class OrderTestCase(BaseTestCase):
    def setUp(self):
        super().setUp() # Call the setUp() method of the BaseTestCase class

        # Add a product to the cart
        self.client.post('/cart/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Create an order
        self.client.post('/order/', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'address_id': 1,
            'payment_id': 1
        })

    def test_create_order(self):
        # Send a POST request to the endpoint
        response = self.client.post('/order/', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'address_id': 1,
            'payment_id': 1
        })

        self.assertEqual(response.status_code, 201)

    def test_get_orders(self):
        # Send a GET request to the endpoint
        response = self.client.get('/order/', headers={'Authorization': 'Bearer ' + self.access_token})

        self.assertEqual(response.status_code, 200)

    def test_get_order(self):
        # Send a GET request to the endpoint
        response = self.client.get('/order/1', headers={'Authorization': 'Bearer ' + self.access_token})

        self.assertEqual(response.status_code, 200)

    def test_get_customer_orders(self):
        # Send a GET request to the endpoint
        response = self.client.get('/order/admin', headers={'Authorization': 'Bearer ' + self.access_token})

        self.assertEqual(response.status_code, 200)

    def test_update_order_status(self):
        # Send a PUT request to the endpoint
        response = self.client.put('/order/admin/1', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'status': 'Delivered'
        })

        self.assertEqual(response.status_code, 200)
