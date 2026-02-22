import unittest
import sys
import os

# Add root directory to sys.path
sys.path.append(os.getcwd())

from app import app

class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_blueprints_registered(self):
        self.assertIn('api', app.blueprints)
        self.assertIn('auth', app.blueprints)
        self.assertIn('admin', app.blueprints)

    def test_api_route(self):
        # API route requires POST
        # If route exists and we send empty JSON, it returns 400 (Invalid JSON or Missing fields)
        response = self.client.post('/api/v1/license/validate', json={})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
