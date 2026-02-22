from functools import wraps
from flask import session, flash, redirect, url_for

def require_admin_auth(f):
    """
    Decorator to protect admin dashboard routes.
    Checks if 'admin_id' is present in the session.
    Redirects to login page with a warning if not found.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Veuillez vous connecter pour accéder au tableau de bord.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
