"""Basic authentication for Flask app"""
from functools import wraps
from flask import session, redirect, url_for, request

def authenticate(username, password):
    """Simple authentication - can be enhanced with proper password hashing"""
    # Basic auth for now
    return username == "admin" and password == "password"

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            if request.endpoint == 'login':
                return f(*args, **kwargs)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function