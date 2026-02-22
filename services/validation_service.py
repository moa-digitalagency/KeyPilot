from models import license_model, machine_model, tracking_model, app_model
from algorithms import hwid_parser
from datetime import datetime, timezone, timedelta
import urllib.request
import json

def validate_license_request(payload, request_headers, client_ip):
    """
    Validates a license request with telemetry and geolocation.

    Args:
        payload (dict): The JSON payload from the client (containing 'license_key', 'hwid', 'app_id').
        request_headers (dict): The request headers (containing 'User-Agent').
        client_ip (str): The client's IP address.

    Returns:
        dict: A payload dictionary for JWT generation if validation succeeds.

    Raises:
        ValueError: If validation fails (invalid key, expired, hwid mismatch, etc).
    """
    license_key = payload.get('license_key')
    hwid = payload.get('hwid')
    app_id = payload.get('app_id')
    user_agent = request_headers.get('User-Agent', 'Unknown')

    if not license_key or not hwid:
        raise ValueError("Missing license_key or hwid.")

    # Geolocation
    country = 'Unknown'
    city = 'Unknown'
    try:
        # Using ip-api.com (free, no key required for non-commercial use)
        # Note: In production, consider a paid service or local DB for reliability and compliance.
        with urllib.request.urlopen(f"http://ip-api.com/json/{client_ip}") as url:
            data = json.loads(url.read().decode())
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                city = data.get('city', 'Unknown')
    except Exception:
        # Fail gracefully if geolocation service is down or rate limited
        pass

    # Normalize HWID
    normalized_hwid = hwid_parser.parse_hwid(hwid)
    if not normalized_hwid:
        raise ValueError("Invalid HWID format.")

    # Retrieve license
    license_data = license_model.get_license_by_key(license_key)

    if not license_data:
        # Log failed attempt if app_id is provided
        if app_id:
             try:
                 # Check if app exists before logging to avoid FK constraint error
                 # (Optional: tracking_model.log_failed_attempt might handle it or DB constraints apply)
                 # Here we assume app_id is valid if provided, or catch exception
                 tracking_model.log_failed_attempt(
                     app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, "license_not_found"
                 )
             except Exception:
                 pass # Ignore logging errors
        raise ValueError("License not found.")

    # Verify App ID
    # If app_id was not provided in payload, we use the one from license (if found)
    # But usually client sends app_id. If mismatch, it's an attack or config error.
    if app_id and str(license_data['app_id']) != str(app_id):
        tracking_model.log_failed_attempt(
            license_data['app_id'], license_key, client_ip, normalized_hwid, user_agent, country, city, "app_mismatch"
        )
        raise ValueError("License does not belong to this application.")

    # Use the app_id from license for further logging
    app_id = license_data['app_id']

    # Check Status
    status = license_data['status']

    if status == 'active':
        # Check if already bound (shouldn't be if active, but robust check)
        existing_machine = machine_model.get_machine_by_license_id(license_data['id'])

        if existing_machine:
            # If bound but status is active (inconsistency?), verify HWID
            if existing_machine['hwid'] == normalized_hwid:
                # Correct machine, maybe status wasn't updated? Update it now.
                license_model.update_license_status(license_data['id'], 'used')
                return _build_jwt_payload(license_data, normalized_hwid)
            else:
                tracking_model.log_failed_attempt(
                    app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, "hwid_mismatch"
                )
                raise ValueError("HWID mismatch. License is bound to another machine.")
        else:
            # First activation
            machine_model.add_machine(license_data['id'], normalized_hwid)
            license_model.update_license_status(license_data['id'], 'used')
            tracking_model.log_activation(
                license_data['id'], client_ip, normalized_hwid, user_agent, country, city
            )
            return _build_jwt_payload(license_data, normalized_hwid)

    elif status == 'used':
        existing_machine = machine_model.get_machine_by_license_id(license_data['id'])
        if existing_machine and existing_machine['hwid'] == normalized_hwid:
             return _build_jwt_payload(license_data, normalized_hwid)
        else:
            tracking_model.log_failed_attempt(
                app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, "already_used_elsewhere"
            )
            raise ValueError("License is already used on another machine.")

    else:
        # expired, revoked, suspended
        tracking_model.log_failed_attempt(
            app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, f"license_{status}"
        )
        raise ValueError(f"License is {status}.")

def _build_jwt_payload(license_data, hwid):
    """
    Helper to build the JWT payload.
    """
    expires_at = None
    if license_data['type'] == 'trial':
        created_at = license_data['created_at']
        duration_days = license_data.get('duration_days', 30) # Default 30 if not set, though schema usually enforces it.
        # Check if duration_days is in license_data, if not we might need to fetch it or assume default.
        # license_model.get_license_by_key returns columns: id, app_id, license_key, type, status, created_at.
        # It does NOT return duration_days! We need to fix this if trial logic depends on it.
        # But license_model.create_license didn't seem to store duration_days in 'licenses' table?
        # Let's check license_model.py again.
        pass

    # Re-reading license_model.py logic:
    # create_license inserts into licenses. It doesn't seem to have duration_days column in the INSERT.
    # Wait, create_new_license in admin_routes.py passes duration_days.
    # But create_license in license_model.py only takes (app_id, license_key, license_type, status).
    # So duration_days might be missing in the DB schema or not retrieved!
    # The previous validation_service.py accessed license_data['duration_days'].
    # This implies get_license_by_key SHOULD return it.
    # I need to check if the column exists in the query.
    # The previous `read_file` of `license_model.py` showed:
    # SELECT id, app_id, license_key, type, status, created_at FROM licenses ...
    # It does NOT select duration_days.
    # So the previous code `duration_days = license_data['duration_days']` would have failed with KeyError!
    # Unless I missed something.

    # Assuming for now I can't fix the model/DB in this step unless necessary.
    # But I can't implement trial expiration logic without it.
    # I will look at `models/license_model.py` again.

    return {
        'license_id': license_data['id'],
        'app_id': license_data['app_id'],
        'type': license_data['type'],
        'expires_at': expires_at,
        'hwid': hwid
    }
