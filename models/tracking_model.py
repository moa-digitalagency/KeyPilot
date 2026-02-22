from config.database import get_db_cursor

def log_activation(license_id, ip_address, mac_address, user_agent, country, city):
    """
    Logs a successful activation.
    Returns the created activation record id.
    """
    query = """
        INSERT INTO activations (license_id, ip_address, mac_address, user_agent, country, city)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (license_id, ip_address, mac_address, user_agent, country, city))
        row = cursor.fetchone()
        return row[0] if row else None

def log_failed_attempt(app_id, attempted_key, ip_address, mac_address, user_agent, country, city, reason):
    """
    Logs a failed activation attempt.
    Returns the created attempt record id.
    """
    query = """
        INSERT INTO failed_attempts (app_id, attempted_key, ip_address, mac_address, user_agent, country, city, reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (app_id, attempted_key, ip_address, mac_address, user_agent, country, city, reason))
        row = cursor.fetchone()
        return row[0] if row else None

def get_activations(app_id=None):
    """
    Lists activation history with license and app details.
    If app_id is provided, filters by app.
    Returns a list of dictionaries.
    """
    query = """
        SELECT
            a.id, a.license_id, a.ip_address, a.mac_address, a.user_agent, a.country, a.city, a.activated_at,
            l.license_key, l.type as license_type,
            ap.name as app_name
        FROM activations a
        JOIN licenses l ON a.license_id = l.id
        JOIN apps ap ON l.app_id = ap.id
    """
    params = []
    if app_id:
        query += " WHERE ap.id = %s"
        params.append(app_id)

    query += " ORDER BY a.activated_at DESC"

    with get_db_cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        activations = []
        for row in rows:
            activations.append({
                'id': row[0],
                'license_id': row[1],
                'ip_address': row[2],
                'mac_address': row[3],
                'user_agent': row[4],
                'country': row[5],
                'city': row[6],
                'activated_at': row[7],
                'license_key': row[8],
                'license_type': row[9],
                'app_name': row[10]
            })
        return activations

def get_failed_attempts(app_id=None):
    """
    Lists failed attempts with app details.
    If app_id is provided, filters by app.
    Returns a list of dictionaries.
    """
    query = """
        SELECT
            f.id, f.app_id, f.attempted_key, f.ip_address, f.mac_address, f.user_agent, f.country, f.city, f.reason, f.attempted_at,
            ap.name as app_name
        FROM failed_attempts f
        JOIN apps ap ON f.app_id = ap.id
    """
    params = []
    if app_id:
        query += " WHERE ap.id = %s"
        params.append(app_id)

    query += " ORDER BY f.attempted_at DESC"

    with get_db_cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        attempts = []
        for row in rows:
            attempts.append({
                'id': row[0],
                'app_id': row[1],
                'attempted_key': row[2],
                'ip_address': row[3],
                'mac_address': row[4],
                'user_agent': row[5],
                'country': row[6],
                'city': row[7],
                'reason': row[8],
                'attempted_at': row[9],
                'app_name': row[10]
            })
        return attempts
