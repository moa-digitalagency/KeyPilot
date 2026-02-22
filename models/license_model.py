from config.database import get_db_cursor

def create_license(app_id, license_key, license_type, duration_days, status="active"):
    """
    Creates a new license.
    Returns the created license as a dictionary.
    """
    query = """
        INSERT INTO licenses (app_id, license_key, type, duration_days, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, app_id, license_key, type, duration_days, status, created_at;
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (app_id, license_key, license_type, duration_days, status))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'app_id': row[1],
                'license_key': row[2],
                'type': row[3],
                'duration_days': row[4],
                'status': row[5],
                'created_at': row[6]
            }
        return None

def get_license_by_key(license_key):
    """
    Retrieves a license by its key.
    Returns a dictionary or None if not found.
    """
    query = """
        SELECT id, app_id, license_key, type, duration_days, status, created_at
        FROM licenses
        WHERE license_key = %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (license_key,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'app_id': row[1],
                'license_key': row[2],
                'type': row[3],
                'duration_days': row[4],
                'status': row[5],
                'created_at': row[6]
            }
        return None

def update_license_status(license_id, status):
    """
    Updates the status of a license.
    Returns True if successful, False otherwise.
    """
    query = "UPDATE licenses SET status = %s WHERE id = %s"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (status, license_id))
        return cursor.rowcount > 0

def get_licenses_by_app_id(app_id):
    """
    Lists all licenses for a specific app.
    Returns a list of dictionaries.
    """
    query = """
        SELECT id, app_id, license_key, type, duration_days, status, created_at
        FROM licenses
        WHERE app_id = %s
        ORDER BY created_at DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (app_id,))
        rows = cursor.fetchall()
        licenses = []
        for row in rows:
            licenses.append({
                'id': row[0],
                'app_id': row[1],
                'license_key': row[2],
                'type': row[3],
                'duration_days': row[4],
                'status': row[5],
                'created_at': row[6]
            })
        return licenses
