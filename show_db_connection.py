"""Show the resolved DATABASE_URL connection string"""
import os
import re
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Mask password for display
    masked_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:*****@', database_url)
    print(f"DATABASE_URL (masked): {masked_url}")
    
    # Parse components
    import urllib.parse
    parsed = urllib.parse.urlparse(database_url)
    print(f"\n=== Connection Details ===")
    print(f"Host: {parsed.hostname}")
    print(f"Port: {parsed.port}")
    print(f"Database: {parsed.path[1:]}")  # Remove leading /
    print(f"User: {parsed.username}")
    print(f"Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
else:
    print("DATABASE_URL is NOT SET")
