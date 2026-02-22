from models import license_model, machine_model, tracking_model, app_model
from algorithms import hwid_parser
from datetime import datetime, timezone, timedelta
import requests
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
        response = requests.get(f"http://ip-api.com/json/{client_ip}", timeout=2)
        if response.status_code == 200:
            data = response.json()
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
                 tracking_model.log_failed_attempt(
                     app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, "license_not_found"
                 )
             except Exception:
                 pass
        raise ValueError("License not found.")

    # Verify App ID
    if app_id and str(license_data['app_id']) != str(app_id):
        tracking_model.log_failed_attempt(
            license_data['app_id'], license_key, client_ip, normalized_hwid, user_agent, country, city, "app_mismatch"
        )
        raise ValueError("License does not belong to this application.")

    app_id = license_data['app_id']

    # Check Status
    status = license_data['status']

    if status == 'active':
        existing_machine = machine_model.get_machine_by_license_id(license_data['id'])

        if existing_machine:
            if existing_machine['hwid'] == normalized_hwid:
                license_model.update_license_status(license_data['id'], 'used')
                return _build_jwt_payload(license_data, normalized_hwid)
            else:
                tracking_model.log_failed_attempt(
                    app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, "hwid_mismatch"
                )
                raise ValueError("HWID mismatch. License is bound to another machine.")
        else:
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
        duration_days = license_data.get('duration_days')
        if duration_days:
            expires_at = (created_at + timedelta(days=duration_days)).isoformat()

    return {
        'license_id': license_data['id'],
        'app_id': license_data['app_id'],
        'type': license_data['type'],
        'expires_at': expires_at,
        'hwid': hwid
    }
