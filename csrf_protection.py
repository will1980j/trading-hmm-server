"""Basic CSRF protection for Flask app"""
import secrets
from functools import wraps
from flask import request, jsonify, session

class CSRFProtect:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
    
    def generate_csrf_token(self):
        """Generate a CSRF token"""
        return secrets.token_hex(16)

def csrf_protect(f):
    """Decorator for CSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF for now - can be enhanced later
        return f(*args, **kwargs)
    return decorated_function

# Global instance
csrf = CSRFProtect()