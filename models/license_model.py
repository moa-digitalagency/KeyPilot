from config.database import get_db_cursor

def create_license(app_id, license_key, license_type, duration_days=None, status="active"):
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

def validate_and_consume_license(license_key, app_secret):
    """
    Validates a license key against an app secret.
    If valid and active, transitions status to 'used'.
    Returns the license dictionary if valid, None otherwise.
    """
    # Join with apps to verify app_secret
    query = """
        SELECT l.id, l.app_id, l.license_key, l.type, l.duration_days, l.status, l.created_at
        FROM licenses l
        JOIN apps a ON l.app_id = a.id
        WHERE l.license_key = %s AND a.app_secret = %s
    """

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (license_key, app_secret))
        row = cursor.fetchone()

        if row:
            license_data = {
                'id': row[0],
                'app_id': row[1],
                'license_key': row[2],
                'type': row[3],
                'duration_days': row[4],
                'status': row[5],
                'created_at': row[6]
            }

            # If active, consume it
            if license_data['status'] == 'active':
                update_query = "UPDATE licenses SET status = 'used' WHERE id = %s"
                cursor.execute(update_query, (license_data['id'],))
                license_data['status'] = 'used'

            return license_data

        return None
