from functools import wraps
from flask import session, request, redirect, url_for, jsonify
from hashlib import sha256
from os import environ

# Simple authentication system
ADMIN_USERNAME = environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = environ.get('ADMIN_PASSWORD_HASH', sha256('changeme123'.encode()).hexdigest())

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def authenticate(username, password):
    # Input validation
    if not username or not password:
        return False
    if not isinstance(username, str) or not isinstance(password, str):
        return False
    if len(username) > 50 or len(password) > 100:
        return False
        
    return (username == ADMIN_USERNAME and 
            hash_password(password) == ADMIN_PASSWORD_HASH)