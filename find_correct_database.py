#!/usr/bin/env python3
"""Find the correct database that Railway is using"""
import os
import psycopg2

# The URL I've been using
old_url = 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway'

# Check the .env file for the correct URL
print("=== CHECKING .env FILE ===")
try:
    with open('.env', 'r') as f:
        for line in f:
            if 'DATABASE_URL' in line:
                print(f"  {line.strip()}")
except Exception as e:
    print(f"  Error reading .env: {e}")

# Check environment variable
print("\n=== ENVIRONMENT VARIABLE ===")
env_url = os.environ.get('DATABASE_URL')
print(f"  DATABASE_URL from env: {env_url}")

# Try connecting to the old URL and check max ID
print("\n=== OLD DATABASE (junction.proxy.rlwy.net:57782) ===")
try:
    conn = psycopg2.connect(old_url)
    cur = conn.cursor()
    cur.execute("SELECT MAX(id), COUNT(*) FROM automated_signals")
    row = cur.fetchone()
    print(f"  Max ID: {row[0]}, Total rows: {row[1]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"  Error: {e}")

# The Railway debug showed IDs in the 130s range, so let's look for a database with that
# Check if there's a different Railway database URL format
print("\n=== CHECKING FOR ALTERNATIVE DATABASE URLS ===")

# Common Railway database URL patterns
alternative_urls = [
    # Try different ports
    'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:5432/railway',
    # Try roundrobin proxy
    'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@roundrobin.proxy.rlwy.net:57782/railway',
]

for url in alternative_urls:
    print(f"\n  Trying: {url[:50]}...")
    try:
        conn = psycopg2.connect(url, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT MAX(id), COUNT(*) FROM automated_signals")
        row = cur.fetchone()
        print(f"    Max ID: {row[0]}, Total rows: {row[1]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
