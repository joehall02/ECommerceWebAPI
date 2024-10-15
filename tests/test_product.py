from base import BaseTestCase
from unittest.mock import patch
from werkzeug.datastructures import FileStorage
import io

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

        # Create a mock image file
        mock_image = FileStorage(
            stream=io.BytesIO(b"fake image data"),
            filename="test_image.jpg",
            content_type="image/jpeg"
        )

        # Create a product image
        with patch('services.product_service.upload_image_to_google_cloud_storage') as mock_upload_image_to_google_cloud_storage:
            mock_upload_image_to_google_cloud_storage.return_value = 'bucket_name/test_image.jpg'
        
            self.client.post(
                '/product/admin/product-image/1', 
                headers={'Authorization': 'Bearer ' + self.access_token}, 
                data={'image': mock_image}, 
                content_type='multipart/form-data'
            )

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

    @patch('services.product_service.upload_image_to_google_cloud_storage')
    def test_create_product_image(self, mock_upload_image_to_google_cloud_storage):
        # Mock the upload_image_to_google_cloud_storage function
        mock_upload_image_to_google_cloud_storage.return_value = 'bucket_name/test_image.jpg'
        
        # Create a mock image file
        mock_image = FileStorage(
            stream=io.BytesIO(b"fake image data"),
            filename="test_image.jpg",
            content_type="image/jpeg"
        )

        # Send a POST request to the endpoint
        response = self.client.post(
            '/product/admin/product-image/1', 
            headers={'Authorization': 'Bearer ' + self.access_token}, 
            data={'image': mock_image}, 
            content_type='multipart/form-data'
        )

        # Check if the response is correct
        self.assertEqual(response.status_code, 201)
        
        # Ensure method is called only once
        mock_upload_image_to_google_cloud_storage.assert_called_once()
    
    def test_get_product_images(self):
        # Send a GET request to the endpoint
        response = self.client.get('/product/product-image/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)


    @patch('services.product_service.remove_image_from_google_cloud_storage')
    def test_delete_product_image(self, mock_remove_image_from_google_cloud_storage):
        # Mock the remove_image_from_google_cloud_storage function
        mock_remove_image_from_google_cloud_storage.return_value = None

        # Send a DELETE request to the endpoint
        response = self.client.delete('/product/admin/product-image/1', headers={'Authorization': 'Bearer ' + self.access_token})

        # Check if the response is correct
        self.assertEqual(response.status_code, 200)

        # Ensure method is called only once
        mock_remove_image_from_google_cloud_storage.assert_called_once()