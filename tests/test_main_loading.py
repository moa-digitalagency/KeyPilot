import unittest
from unittest.mock import patch
import sys
import os

# Add root directory to sys.path
sys.path.append(os.getcwd())

from main import app

class TestMainRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_blueprints_registered(self):
        self.assertIn('api', app.blueprints)
        self.assertIn('auth', app.blueprints)
        self.assertIn('admin', app.blueprints)

    def test_api_route(self):
        # API route requires POST
        response = self.client.post('/api/v1/validate', json={})
        self.assertEqual(response.status_code, 400)

    def test_api_route_alias(self):
        # Alias route check
        response = self.client.post('/api/v1/license/validate', json={})
        self.assertEqual(response.status_code, 400)

    @patch('routes.api_routes.validate_license_request')
    @patch('routes.api_routes.get_app_by_id')
    def test_api_validate_success(self, mock_get_app, mock_validate):
        # Correctly configure mocks
        mock_validate.return_value = {
            'license_id': 1,
            'app_id': 1,
            'hwid': 'test-hwid',
            'type': 'lifetime',
            'expires_at': None
        }
        mock_get_app.return_value = {'app_secret': 'secret'}

        payload = {'license_key': 'key', 'hwid': 'hwid'}
        response = self.client.post('/api/v1/validate', json=payload)

        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertIn('token', response.get_json())
