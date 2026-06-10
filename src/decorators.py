from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    """Restricts access to administrators."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """Restricts access to super administrators only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_superadmin', False):
            flash('Acceso denegado. Solo el super administrador puede realizar esta acción.', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function
