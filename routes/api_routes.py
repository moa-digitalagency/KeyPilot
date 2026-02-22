from flask import Blueprint, request, jsonify
from services.validation_service import validate_license_request
from models.app_model import get_app_by_id
from security.jwt_handler import generate_token

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/v1/validate', methods=['POST'])
def validate():
    """
    Validates a license key.
    Expects JSON payload with 'license_key', 'hwid', and optionally 'app_id'.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract client info
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    # If multiple IPs in X-Forwarded-For, take the first one
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()

    # Extract headers
    headers = {
        'User-Agent': request.headers.get('User-Agent')
    }

    try:
        # Validate license
        # Returns a payload suitable for JWT
        jwt_payload = validate_license_request(data, headers, client_ip)

        # Get app_id from the result to fetch the secret
        app_id = jwt_payload.get('app_id')
        if not app_id:
             # Should not happen if validation succeeds
             return jsonify({'error': 'Internal server error: App ID missing'}), 500

        # Get app secret for signing the JWT
        app = get_app_by_id(app_id)
        if not app:
             return jsonify({'error': 'App not found'}), 404

        secret = app['app_secret']

        # Generate token
        token = generate_token(jwt_payload, secret)

        return jsonify({'token': token})

    except ValueError as e:
        # validation_service raises ValueError for invalid/expired licenses
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        # Log the error in a real scenario
        print(f"Error validating license: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Alias for backward compatibility (optional but recommended)
@api_bp.route('/api/v1/license/validate', methods=['POST'])
def validate_alias():
    return validate()
