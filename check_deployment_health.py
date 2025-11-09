#!/usr/bin/env python3
"""
Check Railway deployment health and database connectivity
"""

import requests
import json

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 60)
print("🔍 RAILWAY DEPLOYMENT HEALTH CHECK")
print("=" * 60)
print()

# Test 1: Check if server is running
print("TEST 1: Server Status")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"✅ Server is running (Status: {response.status_code})")
except Exception as e:
    print(f"❌ Server not responding: {e}")
    exit(1)

print()

# Test 2: Check database status
print("TEST 2: Database Connection")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/api/db-status", timeout=10)
    data = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('status') == 'connected':
        print("✅ Database is connected")
    else:
        print(f"❌ Database issue: {data.get('message', 'Unknown')}")
except Exception as e:
    print(f"❌ Database check failed: {e}")

print()

# Test 3: Check webhook endpoint exists
print("TEST 3: Webhook Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/api/automated-signals", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 405:  # Method Not Allowed (GET on POST endpoint)
        print("✅ Webhook endpoint exists (returns 405 for GET, expects POST)")
    elif response.status_code == 200:
        print(f"✅ Webhook endpoint exists: {response.json()}")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Webhook check failed: {e}")

print()

# Test 4: Check if automated_signals table exists
print("TEST 4: Automated Signals Table")
print("-" * 60)
try:
    response = requests.post(
        f"{BASE_URL}/api/create-automated-signals-table",
        json={},
        timeout=15
    )
    data = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get('success'):
        print(f"✅ Table ready ({data.get('columns', 0)} columns)")
    else:
        print(f"❌ Table creation failed: {data.get('error', 'Unknown')}")
except Exception as e:
    print(f"❌ Table check failed: {e}")

print()
print("=" * 60)
print("HEALTH CHECK COMPLETE")
print("=" * 60)
