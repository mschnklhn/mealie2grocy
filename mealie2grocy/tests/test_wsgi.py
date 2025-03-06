import unittest
from wsgi import app

class BasicTests(unittest.TestCase):

    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        # Test the home page route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mealie2Grocy', response.data)


if __name__ == "__main__":
    unittest.main()
