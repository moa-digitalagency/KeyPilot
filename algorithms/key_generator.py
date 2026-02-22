import secrets
import string

def generate_license_key():
    """
    Generates a unique license key in the format XXXX-XXXX-XXXX-XXXX.
    Uses cryptographically secure random number generator.
    """
    characters = string.ascii_uppercase + string.digits
    groups = []
    for _ in range(4):
        group = "".join(secrets.choice(characters) for _ in range(4))
        groups.append(group)

    return "-".join(groups)
