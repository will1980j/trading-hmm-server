#!/usr/bin/env python3
"""
Direct test of the automated signals webhook with detailed error reporting
"""

import requests
import json
import time

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 70)
print("🧪 DIRECT WEBHOOK TEST")
print("=" * 70)
print()

# Wait a moment for deployment
print("⏳ Waiting 10 seconds for deployment to stabilize...")
time.sleep(10)
print()

# Test payload
payload = {
    "event_type": "ENTRY",
    "trade_id": "DIRECT_TEST_001",
    "direction": "LONG",
    "entry_price": 21250.5,
    "stop_loss": 21225.5,
    "session": "NY AM",
    "bias": "Bullish",
    "timestamp": int(time.time() * 1000),
    "account_size": 100000,
    "risk_percent": 0.25,
    "contracts": 4,
    "risk_amount": 250.0
}

print("📤 Sending ENTRY signal to webhook...")
print(f"URL: {BASE_URL}/api/automated-signals")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/api/automated-signals",
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📥 Response received:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()
    
    try:
        data = response.json()
        print(f"JSON Response:")
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200 and data.get('success'):
            print()
            print("✅ SUCCESS! Webhook is working!")
            print(f"Signal ID: {data.get('signal_id')}")
            print(f"Trade ID: {data.get('trade_id')}")
        else:
            print()
            print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
            
    except json.JSONDecodeError:
        print(f"Raw Response (not JSON):")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print()
print("=" * 70)
