import unittest
from flask import Flask, session
import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from config.settings import Config

class TestAuthMiddlewareRedirect(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder='../templates')
        self.app.config.from_object(Config)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    def test_unauthorized_access_redirects_with_flash(self):
        # Ensure no admin_id in session
        with self.client.session_transaction() as sess:
            if 'admin_id' in sess:
                del sess['admin_id']

        # Access protected route, following redirects to catch the rendered flash message on login page
        response = self.client.get('/dashboard', follow_redirects=True)

        # Check that we landed on the login page (200 OK)
        self.assertEqual(response.status_code, 200)

        # Check that the flash message is present in the response content
        # Note: bytes must be decoded or compared with bytes
        expected_message = "Veuillez vous connecter pour accéder au tableau de bord.".encode('utf-8')
        self.assertIn(expected_message, response.data)

        # Also check we are on the login page by looking for some unique text
        self.assertIn(b'Bienvenue sur KeyPilot', response.data)

if __name__ == '__main__':
    unittest.main()
