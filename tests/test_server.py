import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

from server import app


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    @patch('server.check_auth')
    @patch('server.update_products_in_mealie')
    def test_update_mealie_products(self, mock_update_products, mock_check_auth):
        mock_check_auth.return_value = True
        response = self.app.get('/update-mealie-products')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_update_products.called)
        self.assertIn(b'{"success":true}', response.data)

    @patch('server.check_auth')
    @patch('server.update_grocy_shoppinglist_from_mealie')
    def test_update_grocy_shoppinglist(self, mock_update_shoppinglist, mock_check_auth):
        mock_check_auth.return_value = True
        mock_update_shoppinglist.return_value = 'Sample Result'
        response = self.app.get('/update-grocy-shoppinglist')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_update_shoppinglist.called)
        self.assertIn(b'"success":true', response.data)
        self.assertIn(b'Sample Result', response.data)

    @patch('server.check_auth')
    @patch('server.compare_product_databases')
    def test_compare_product_databases(self, mock_compare_databases, mock_check_auth):
        mock_check_auth.return_value = True
        mock_compare_databases.return_value = 'Comparison Result'
        response = self.app.get('/compare-product-databases')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_compare_databases.called)
        self.assertIn(b'"success":true', response.data)
        self.assertIn(b'Comparison Result', response.data)

    @patch('server.test_grocy_connection')
    @patch('server.test_mealie_connection')
    def test_health_check(self, mock_mealie_connection, mock_grocy_connection):
        mock_grocy_connection.return_value = True
        mock_mealie_connection.return_value = True
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"status":"alive"', response.data)

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Mealie2Grocy</title>', response.data)  # Assuming there's a title in index.html

    @patch('server.check_auth')
    def test_unauthorized_access(self, mock_check_auth):
        mock_check_auth.return_value = False
        response = self.app.get('/update-mealie-products')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'"error":"Unauthorized"', response.data)

if __name__ == '__main__':
    unittest.main()