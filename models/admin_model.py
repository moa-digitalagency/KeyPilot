from config.database import get_db_cursor
from werkzeug.security import check_password_hash

def find_admin_by_username(username):
    """
    Finds an admin by username.
    Returns a dictionary representing the admin if found, else None.
    """
    query = "SELECT id, username, password_hash FROM admins WHERE username = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password_hash': row[2]
            }
        return None

def verify_password(stored_password_hash, provided_password):
    """
    Verifies a password against a stored hash.
    Returns True if the password matches, else False.
    """
    return check_password_hash(stored_password_hash, provided_password)
