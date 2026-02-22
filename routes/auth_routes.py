from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.admin_model import find_admin_by_username, verify_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Please enter both username and password')
        return redirect(url_for('auth.login'))

    admin = find_admin_by_username(username)

    if admin and verify_password(admin['password_hash'], password):
        session['admin_id'] = admin['id']
        return redirect(url_for('admin.dashboard'))

    flash('Invalid username or password')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
