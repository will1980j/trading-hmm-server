#!/usr/bin/env python3
"""
CSRF Protection for Trading System
"""

from secrets import token_hex, compare_digest
from hashlib import sha256
from functools import wraps
from flask import request, session, abort, jsonify

# Constants
PROTECTED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

class CSRFProtection:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        CSRF_TOKEN_TIMEOUT = 3600  # 1 hour
        app.config.setdefault('CSRF_SECRET_KEY', token_hex(32))
        app.config.setdefault('CSRF_TOKEN_TIMEOUT', CSRF_TOKEN_TIMEOUT)
        
    def generate_csrf_token(self):
        """Generate a new CSRF token"""
        try:
            if 'csrf_token' not in session:
                session['csrf_token'] = token_hex(32)
            return session['csrf_token']
        except Exception:
            return token_hex(32)
    
    def validate_csrf_token(self, token):
        """Validate CSRF token"""
        if 'csrf_token' not in session:
            return False
        return compare_digest(session['csrf_token'], token)

def csrf_protect(f):
    """Decorator to protect routes with CSRF validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in PROTECTED_METHODS:
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not token or not csrf.validate_csrf_token(token):
                return jsonify({'error': 'CSRF token missing or invalid'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Global CSRF instance
csrf = CSRFProtection()