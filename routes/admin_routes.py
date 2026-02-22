from flask import Blueprint, render_template, request, redirect, url_for, flash
from security.auth_middleware import require_admin_auth
from services.app_service import register_app
from services.license_service import create_new_license
from models.app_model import list_apps

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@require_admin_auth
def before_request():
    pass

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
