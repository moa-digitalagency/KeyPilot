from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from config.settings import Config

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
        session['admin_id'] = 'superadmin'
        return redirect(url_for('admin.dashboard'))

    flash('Invalid username or password')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
