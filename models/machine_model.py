from config.database import get_db_cursor

def add_machine(license_id, hwid):
    """
    Links a HWID to a license.
    Returns the created machine record as a dictionary.
    """
    query = """
        INSERT INTO machines (license_id, hwid)
        VALUES (%s, %s)
        RETURNING id, license_id, hwid, activated_at;
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (license_id, hwid))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'license_id': row[1],
                'hwid': row[2],
                'activated_at': row[3]
            }
        return None

def check_hwid_match(hwid, license_id):
    """
    Checks if a HWID corresponds to a specific license.
    Returns True if a match is found, else False.
    """
    query = "SELECT 1 FROM machines WHERE hwid = %s AND license_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (hwid, license_id))
        return cursor.fetchone() is not None

def get_machine_by_license_id(license_id):
    """
    Retrieves the machine associated with a license ID.
    Returns a dictionary or None if not found.
    """
    query = """
        SELECT id, license_id, hwid, activated_at
        FROM machines
        WHERE license_id = %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (license_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'license_id': row[1],
                'hwid': row[2],
                'activated_at': row[3]
            }
        return None
