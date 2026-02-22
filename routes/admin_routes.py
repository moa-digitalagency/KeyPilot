from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from security.auth_middleware import require_admin_auth
from services.app_service import register_app
from services.license_service import create_new_license
from models.app_model import list_apps
from utils.snippet_builder import generate_client_snippet

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@require_admin_auth
def before_request():
    pass

@admin_bp.route('/dashboard')
def dashboard():
    apps = list_apps()
    stats = {
        'total_apps': len(apps),
        'total_licenses': 'N/A', # Placeholder as we don't have a global count yet
        'active_licenses': 'N/A'
    }
    return render_template('dashboard.html', stats=stats, recent_apps=apps[:5])

@admin_bp.route('/snippet/<app_id>')
def get_snippet(app_id):
    # Construct API URL from request.host_url, ensuring no trailing slash
    api_url = request.host_url.rstrip('/')
    snippet = generate_client_snippet(app_id, api_url)
    return jsonify({'snippet': snippet})

@admin_bp.route('/apps')
def apps():
    apps_list = list_apps()
    return render_template('apps.html', apps=apps_list)

@admin_bp.route('/apps/new', methods=['POST'])
def new_app():
    name = request.form.get('name')
    if name:
        try:
            register_app(name)
            flash('App created successfully')
        except Exception as e:
            flash(f'Error creating app: {str(e)}')
    else:
        flash('App name is required')
    return redirect(url_for('admin.apps'))

@admin_bp.route('/licenses/generate', methods=['POST'])
def generate_license():
    app_id = request.form.get('app_id')
    license_type = request.form.get('type')
    duration_days_str = request.form.get('duration_days')

    if not app_id or not license_type:
        flash('Missing required fields')
        return redirect(url_for('admin.apps'))

    try:
        duration_days = None
        if duration_days_str and duration_days_str.strip():
            duration_days = int(duration_days_str)

        license_data = create_new_license(app_id, license_type, duration_days)
        flash(f'License created: {license_data["license_key"]}')

    except ValueError as e:
        flash(str(e))
    except Exception as e:
        flash('An error occurred while generating license')
        print(f"Error generating license: {e}")

    return redirect(url_for('admin.apps'))
