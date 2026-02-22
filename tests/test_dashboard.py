import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session
import sys
import os

# Ensure the app can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder='../templates')
        self.app.secret_key = 'test_secret'
        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    @patch('routes.admin_routes.list_apps')
    def test_dashboard_route(self, mock_list_apps):
        # Mock apps data
        mock_list_apps.return_value = [
            {'id': 1, 'name': 'App1', 'app_secret': 'secret123456789', 'created_at': '2023-01-01'},
            {'id': 2, 'name': 'App2', 'app_secret': 'secret987654321', 'created_at': '2023-01-02'}
        ]

        # Simulate admin login
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1

        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)

        # Check for key elements in the new dashboard HTML
        self.assertIn(b'Vue d\'ensemble', response.data)
        self.assertIn(b'Total Applications', response.data)
        self.assertIn(b'Licences Totales', response.data)
        self.assertIn(b'Licences Actives', response.data)
        self.assertIn(b'Tentatives Bloqu\xc3\xa9es', response.data) # Bloquées in utf-8

        # Check if stats are rendered (N/A for now as per backend)
        self.assertIn(b'N/A', response.data)

        # Check if apps are listed
        self.assertIn(b'App1', response.data)
        self.assertIn(b'App2', response.data)

if __name__ == '__main__':
    unittest.main()
