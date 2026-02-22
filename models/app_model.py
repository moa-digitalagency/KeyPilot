from config.database import get_db_cursor

def create_app(name, app_secret):
    """
    Creates a new app.
    Returns the created app as a dictionary.
    """
    query = """
        INSERT INTO apps (name, app_secret)
        VALUES (%s, %s)
        RETURNING id, name, app_secret, created_at;
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (name, app_secret))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'app_secret': row[2],
                'created_at': row[3]
            }
        return None

def list_apps():
    """
    Lists all apps.
    Returns a list of dictionaries.
    """
    query = "SELECT id, name, app_secret, created_at FROM apps ORDER BY created_at DESC"
    with get_db_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        apps = []
        for row in rows:
            apps.append({
                'id': row[0],
                'name': row[1],
                'app_secret': row[2],
                'created_at': row[3]
            })
        return apps

def get_app_by_id(app_id):
    """
    Retrieves an app by its ID.
    Returns a dictionary or None if not found.
    """
    query = "SELECT id, name, app_secret, created_at FROM apps WHERE id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (app_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'app_secret': row[2],
                'created_at': row[3]
            }
        return None
