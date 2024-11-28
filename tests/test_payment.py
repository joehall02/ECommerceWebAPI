from base import BaseTestCase

# Tests for all payment related endpoints
class PaymentTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    # Payment tests
    def test_create_payment(self):
        # Send a POST request to the endpoint
        response = self.client.post('/payment/', headers={'Authorization': 'Bearer ' + self.access_token}, json={
            'stripe_payment_id': 'Test_stripe_payment_id'
        })

        self.assertEqual(response.status_code, 201)

    def test_get_payments(self):
        # Send a GET request to the endpoint
        response = self.client.get('/payment/', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_get_payment(self):
        # Send a GET request to the endpoint
        response = self.client.get('/payment/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

    def test_delete_payment(self):
        # Send a DELETE request to the endpoint
        response = self.client.delete('/payment/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)