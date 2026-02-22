from functools import wraps
from flask import session, abort

def require_admin_auth(f):
    """
    Decorator to protect admin dashboard routes.
    Checks if 'admin_id' is present in the session.
    Aborts with 401 Unauthorized if not found.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            # Session invalid or missing admin_id
            # In a real application, you might want to redirect to a login page here.
            # e.g., return redirect(url_for('login'))
            abort(401)
        return f(*args, **kwargs)
    return decorated_function
