from models import license_model, machine_model
from algorithms import hwid_parser
from datetime import datetime, timezone, timedelta

def validate_license(app_id, license_key, hwid):
    """
    Validates a license key for a given app and HWID.

    Args:
        app_id (int): The ID of the application.
        license_key (str): The license key to validate.
        hwid (str): The raw Hardware ID.

    Returns:
        dict: A payload dictionary for JWT generation if validation succeeds.

    Raises:
        ValueError: If validation fails (invalid key, expired, hwid mismatch, etc).
    """
    # Normalize and hash the HWID
    normalized_hwid = hwid_parser.parse_hwid(hwid)
    if not normalized_hwid:
        raise ValueError("Invalid HWID format.")

    # Retrieve the license
    license_data = license_model.get_license_by_key(license_key)
    if not license_data:
        raise ValueError("License not found.")

    # Verify App ID
    if license_data['app_id'] != app_id:
        raise ValueError("License does not belong to this application.")

    # Check Status
    if license_data['status'] != 'active':
        raise ValueError(f"License is {license_data['status']}.")

    # Check Expiration for Trial Licenses
    expires_at = None
    if license_data['type'] == 'trial':
        created_at = license_data['created_at']
        duration_days = license_data['duration_days']

        # Ensure created_at is timezone aware (assume UTC if naive)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        expiration_date = created_at + timedelta(days=duration_days)
        expires_at = expiration_date.isoformat()

        # Check if expired
        if datetime.now(timezone.utc) > expiration_date:
            license_model.update_license_status(license_data['id'], 'expired')
            raise ValueError("Trial license has expired.")

    # Handle HWID Binding
    existing_machine = machine_model.get_machine_by_license_id(license_data['id'])

    if existing_machine:
        # License is already bound, check if HWID matches
        if existing_machine['hwid'] != normalized_hwid:
            raise ValueError("HWID mismatch. License is bound to another machine.")
    else:
        # First activation: Bind the HWID to the license
        machine_model.add_machine(license_data['id'], normalized_hwid)

    # Return payload for JWT
    return {
        'license_id': license_data['id'],
        'app_id': license_data['app_id'],
        'type': license_data['type'],
        'expires_at': expires_at,
        'hwid': normalized_hwid
    }
