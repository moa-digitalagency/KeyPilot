import sys
import os

# Ensure the root directory is in sys.path so config can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db_cursor

def init_db():
    """
    Initializes the database by creating the necessary tables.
    """
    print("Initializing database...")
    try:
        with get_db_cursor(commit=True) as cursor:
            # Create apps table
            print("Creating 'apps' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apps (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    app_secret VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create licenses table
            print("Creating 'licenses' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    id SERIAL PRIMARY KEY,
                    app_id INTEGER REFERENCES apps(id) ON DELETE CASCADE,
                    license_key VARCHAR(255) UNIQUE NOT NULL,
                    type VARCHAR(50) CHECK (type IN ('trial', 'lifetime')) NOT NULL,
                    status VARCHAR(50) CHECK (status IN ('active', 'used', 'revoked')) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create activations table
            print("Creating 'activations' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activations (
                    id SERIAL PRIMARY KEY,
                    license_id INTEGER REFERENCES licenses(id) ON DELETE CASCADE,
                    ip_address VARCHAR(255),
                    mac_address VARCHAR(255),
                    user_agent VARCHAR(255),
                    country VARCHAR(100),
                    city VARCHAR(100),
                    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create failed_attempts table
            print("Creating 'failed_attempts' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_attempts (
                    id SERIAL PRIMARY KEY,
                    app_id INTEGER REFERENCES apps(id) ON DELETE CASCADE,
                    attempted_key VARCHAR(255),
                    ip_address VARCHAR(255),
                    mac_address VARCHAR(255),
                    user_agent VARCHAR(255),
                    country VARCHAR(100),
                    city VARCHAR(100),
                    reason VARCHAR(255),
                    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        print("Database initialized successfully.")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
