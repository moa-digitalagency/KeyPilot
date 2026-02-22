from flask import Flask, redirect, url_for, request, session, render_template, flash, Blueprint
from werkzeug.security import check_password_hash
from config.settings import Config
from routes.api_routes import api_bp
from routes.admin_routes import admin_bp

app = Flask(__name__, static_folder='statics')
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY # Ensure secret key is set for sessions

# Define Auth Blueprint locally to use .env based auth
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    admin_username = Config.ADMIN_USERNAME
    admin_password_hash = Config.ADMIN_PASSWORD_HASH

    if not username or not password:
        flash('Please enter both username and password')
        return redirect(url_for('auth.login'))

    if username == admin_username and check_password_hash(admin_password_hash, password):
        session['admin_id'] = 'superadmin' # satisfying require_admin_auth
        return redirect(url_for('admin.dashboard'))

    flash('Invalid username or password')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return redirect(url_for('admin.dashboard'))

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
