import sys
import os

# Add the project root directory to the Python path to allow imports from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db_cursor

def init_db():
    """
    Initializes the database by creating the necessary tables.
    """
    print("Initializing database...")
    try:
        with get_db_cursor(commit=True) as cursor:
            # Create admins table
            print("Creating 'admins' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                );
            """)

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
                    duration_days INTEGER,
                    status VARCHAR(50) CHECK (status IN ('active', 'revoked', 'expired')) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create machines table
            print("Creating 'machines' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS machines (
                    id SERIAL PRIMARY KEY,
                    license_id INTEGER REFERENCES licenses(id) ON DELETE CASCADE,
                    hwid VARCHAR(255) UNIQUE NOT NULL,
                    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        print("Database initialized successfully.")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
