"""Basic authentication for Flask app"""
from functools import wraps
from flask import session, redirect, url_for, request

def authenticate(username, password):
    """Authentication with password hashing"""
    import hashlib
    import os
    
    # Check if environment variable for hash exists
    stored_hash = os.environ.get('ADMIN_PASSWORD_HASH')
    
    if stored_hash:
        # Use hashed password from environment
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return username == "admin" and password_hash == stored_hash
    else:
        # Fallback to plain text for local development
        return username == "admin" and password == "n2351447"

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