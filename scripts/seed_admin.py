import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db_cursor
from werkzeug.security import generate_password_hash

def seed_admin():
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if admin exists
            cursor.execute("SELECT id FROM admins WHERE username = %s", ('admin',))
            if cursor.fetchone():
                print("Admin already exists.")
                return

            hashed_pw = generate_password_hash('admin')
            cursor.execute("INSERT INTO admins (username, password_hash) VALUES (%s, %s)", ('admin', hashed_pw))
            print("Admin user 'admin' created with password 'admin'.")
    except Exception as e:
        print(f"Error seeding admin: {e}")

if __name__ == '__main__':
    seed_admin()
