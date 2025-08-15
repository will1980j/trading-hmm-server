import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Get current environment variables
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_hash = os.environ.get('ADMIN_PASSWORD_HASH', hashlib.sha256('changeme123'.encode()).hexdigest())

print("=== AUTH DEBUG ===")
print(f"Admin Username: '{admin_username}'")
print(f"Admin Hash: {admin_hash}")
print()

# Test some passwords
test_passwords = ['admin', 'changeme123', 'tradingempire25', 'TradingEmpire25']

for password in test_passwords:
    generated_hash = hash_password(password)
    matches = generated_hash == admin_hash
    print(f"Password: '{password}'")
    print(f"Generated: {generated_hash}")
    print(f"Matches: {matches}")
    print()

print("Try these credentials:")
print(f"Username: {admin_username}")
print("Password: One of the passwords that shows 'Matches: True'")