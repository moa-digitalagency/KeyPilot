import hashlib

def parse_hwid(hwid_raw):
    """
    Cleans, normalizes, and hashes an HWID string.

    Args:
        hwid_raw (str): The raw HWID string.

    Returns:
        str: The SHA-256 hash of the normalized HWID.
    """
    if not hwid_raw:
        return None

    # Normalize: strip whitespace and convert to lowercase
    normalized_hwid = hwid_raw.strip().lower()

    # Hash using SHA-256
    hashed_hwid = hashlib.sha256(normalized_hwid.encode('utf-8')).hexdigest()

    return hashed_hwid
