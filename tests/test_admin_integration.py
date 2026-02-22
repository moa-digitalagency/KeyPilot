import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session
# We must import admin_bp to register it, but we also want to patch imports inside it.
# Patching imports already imported via 'from ... import ...' requires patching the module where they are used.

# Make sure we can import the app modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp

class TestAdminIntegration(unittest.TestCase):
    def setUp(self):
        # We need to point template folder correctly
        self.app = Flask(__name__, template_folder='../templates')
        self.app.secret_key = 'test_secret'
        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    @patch('routes.admin_routes.get_activations')
    def test_users_route(self, mock_get_activations):
        # Mock data
        mock_get_activations.return_value = [
            {'activated_at': '2023-01-01', 'app_name': 'TestApp', 'ip_address': '127.0.0.1', 'mac_address': 'hwid', 'country': 'US', 'city': 'NY', 'license_key': 'KEY-1234', 'license_type': 'lifetime'}
        ]

        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1

        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Activations', response.data)

    @patch('routes.admin_routes.get_failed_attempts')
    def test_attempts_route(self, mock_get_attempts):
        mock_get_attempts.return_value = []

        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1

        response = self.client.get('/attempts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tentatives de Fraude', response.data)

    def test_settings_route(self):
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1

        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Param\xc3\xa8tres', response.data) # Paramètres in bytes utf-8

if __name__ == '__main__':
    unittest.main()
