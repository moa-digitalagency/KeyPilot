import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Config:
    """
    Configuration class to load environment variables.
    """
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

    # Database
    # Support both full URL and individual components
    DATABASE_URL = os.getenv('DATABASE_URL')

    DB_NAME = os.getenv('DB_NAME', 'keypilot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
