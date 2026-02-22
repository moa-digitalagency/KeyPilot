import sys
import os
import threading
import time
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from playwright.sync_api import sync_playwright

# Add current directory to path to find templates
sys.path.append(os.getcwd())

app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), 'templates'),
            static_folder=os.path.join(os.getcwd(), 'static'))
app.secret_key = 'test_secret'

# Mock blueprint
from flask import Blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    stats = {
        'total_apps': 5,
        'total_licenses': 120,
        'active_licenses': 95
    }
    recent_apps = [
        {'id': 1, 'name': 'App 1', 'app_secret': 'secret1', 'created_at': '2023-10-01'},
        {'id': 2, 'name': 'App 2', 'app_secret': 'secret2', 'created_at': '2023-10-05'}
    ]
    return render_template('dashboard.html', stats=stats, recent_apps=recent_apps)

@admin_bp.route('/apps')
def apps():
    apps_list = [
        {'id': 1, 'name': 'App 1', 'app_secret': 'secret1', 'created_at': '2023-10-01'},
        {'id': 2, 'name': 'App 2', 'app_secret': 'secret2', 'created_at': '2023-10-05'}
    ]
    return render_template('apps.html', apps=apps_list)

@admin_bp.route('/apps/<int:app_id>')
def app_detail(app_id):
    app = {'id': app_id, 'name': f'App {app_id}', 'app_secret': 'XXXX-YYYY-ZZZZ', 'created_at': '2023-10-01'}
    ai_prompt = "# Prompt Instructeur\n..."
    return render_template('app_detail.html', app=app, ai_prompt=ai_prompt)

@admin_bp.route('/users')
def users():
    activations = [
        {'id': 1, 'activated_at': '2023-10-26 10:00:00', 'app_name': 'App 1', 'ip_address': '192.168.1.1', 'mac_address': '00:11:22:33:44:55', 'city': 'Paris', 'country': 'FR', 'license_key': 'AAAA-BBBB-CCCC-DDDD', 'license_type': 'lifetime'}
    ]
    return render_template('users.html', activations=activations)

@admin_bp.route('/attempts')
def attempts():
    attempts_list = [
        {'id': 1, 'attempted_at': '2023-10-26 11:00:00', 'app_name': 'App 1', 'ip_address': '10.0.0.1', 'country': 'US', 'city': 'New York', 'user_agent': 'Mozilla/5.0', 'attempted_key': 'BAD-KEY', 'reason': 'Invalid Key'}
    ]
    return render_template('attempts.html', attempts=attempts_list)

@admin_bp.route('/settings')
def settings():
    return render_template('settings.html')

app.register_blueprint(admin_bp, url_prefix='/admin')

# Mock auth logout
@app.route('/logout')
def logout():
    return 'Logged out'
# Mock url_for('auth.logout') needs an endpoint 'auth.logout'
auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/logout')
def logout():
    return 'Logged out'
app.register_blueprint(auth_bp, url_prefix='/auth')

# Run Flask in a separate thread
def run_app():
    # Bind to 0.0.0.0 to ensure accessibility if needed, though localhost works for playwright in same container
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == "__main__":
    print("Starting Flask app...")
    threading.Thread(target=run_app, daemon=True).start()
    time.sleep(2) # Wait for server to start

    # Playwright script
    print("Starting Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Dashboard (Base template check)
        try:
            print("Checking Dashboard...")
            page.goto('http://127.0.0.1:5000/admin/dashboard')
            page.screenshot(path='verification/dashboard.png', full_page=True)
            print("Dashboard screenshot taken.")
        except Exception as e:
            print(f"Error checking dashboard: {e}")

        # 2. App Detail
        try:
            print("Checking App Detail...")
            page.goto('http://127.0.0.1:5000/admin/apps/1')
            page.screenshot(path='verification/app_detail.png', full_page=True)
            print("App Detail screenshot taken.")
        except Exception as e:
            print(f"Error checking app detail: {e}")

        # 3. Users
        try:
            print("Checking Users...")
            page.goto('http://127.0.0.1:5000/admin/users')
            page.screenshot(path='verification/users.png', full_page=True)
            print("Users screenshot taken.")
        except Exception as e:
            print(f"Error checking users: {e}")

        # 4. Attempts
        try:
            print("Checking Attempts...")
            page.goto('http://127.0.0.1:5000/admin/attempts')
            page.screenshot(path='verification/attempts.png', full_page=True)
            print("Attempts screenshot taken.")
        except Exception as e:
            print(f"Error checking attempts: {e}")

        # 5. Settings
        try:
            print("Checking Settings...")
            page.goto('http://127.0.0.1:5000/admin/settings')
            page.screenshot(path='verification/settings.png', full_page=True)
            print("Settings screenshot taken.")
        except Exception as e:
            print(f"Error checking settings: {e}")

        browser.close()
