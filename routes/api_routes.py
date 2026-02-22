from flask import Blueprint, request, jsonify
from services.validation_service import validate_license
from models.app_model import get_app_by_id
from security.jwt_handler import generate_token

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/v1/license/validate', methods=['POST'])
def validate():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    app_id = data.get('app_id')
    license_key = data.get('license_key')
    hwid = data.get('hwid')

    if not app_id or not license_key or not hwid:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Validate license
        # Note: validate_license returns a dict payload suitable for JWT
        payload = validate_license(app_id, license_key, hwid)

        # Get app secret for signing the JWT
        app = get_app_by_id(app_id)
        if not app:
             return jsonify({'error': 'App not found'}), 404

        secret = app['app_secret']

        # Generate token
        token = generate_token(payload, secret)

        return jsonify({'token': token})

    except ValueError as e:
        # validation_service raises ValueError for invalid/expired licenses
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        # Log the error in a real scenario
        print(f"Error validating license: {e}")
        return jsonify({'error': 'Internal server error'}), 500
