from models import license_model
from algorithms import key_generator

def create_new_license(app_id, license_type, duration_days=None):
    """
    Creates a new license for the given app.

    Args:
        app_id (int): The ID of the application.
        license_type (str): 'trial' or 'lifetime'.
        duration_days (int, optional): Duration in days for trial licenses.

    Returns:
        dict: The created license.

    Raises:
        ValueError: If inputs are invalid.
    """
    if license_type not in ('trial', 'lifetime'):
        raise ValueError("Invalid license type. Must be 'trial' or 'lifetime'.")

    if license_type == 'trial':
        if not duration_days or duration_days <= 0:
            raise ValueError("Trial licenses must have a positive duration in days.")
    elif license_type == 'lifetime':
        # For lifetime, duration is not applicable, ensure it is treated as such
        # We can set it to None or a sentinel value, depending on what the DB expects.
        # The DB schema allows NULL? Let's assume yes or that None becomes NULL.
        # Looking at schema: duration_days INTEGER (no NOT NULL constraint mentioned in snippet, but in init_db it was just INTEGER)
        # Let's pass None.
        duration_days = None

    # Generate a unique license key
    license_key = key_generator.generate_license_key()

    # Create the license in the database
    return license_model.create_license(app_id, license_key, license_type, duration_days)
