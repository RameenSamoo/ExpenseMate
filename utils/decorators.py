from functools import wraps
from flask import session, jsonify, redirect, url_for, request

def login_required(f):
    """
    Decorator for protecting endpoints.
    Returns JSON 401 Unauthorized for API requests,
    or redirects to /login for view requests.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required. Please log in.'}), 401
            return redirect(url_for('auth_routes.login_view'))
        return f(*args, **kwargs)
    return decorated_function
