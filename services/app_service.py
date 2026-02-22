import os
from models import app_model

def register_app(name):
    """
    Registers a new application.
    Generates a secure random app_secret using os.urandom.
    Calls app_model to store the application.
    """
    if not name:
        raise ValueError("App name cannot be empty")

    # Generate a 32-byte (64 character hex) secret
    app_secret = os.urandom(32).hex()

    return app_model.create_app(name, app_secret)
