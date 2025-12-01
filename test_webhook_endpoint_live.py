#!/usr/bin/env python3
"""Test if the webhook endpoint is responding"""
import requests
import json

# Test the webhook endpoint with a test payload
webhook_url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/webhook'

# Test GET (should fail or return method not allowed)
print("=== Testing GET request ===")
try:
    resp = requests.get(webhook_url, timeout=10)
    print(f"GET Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"GET Error: {e}")

# Test POST with empty body
print("\n=== Testing POST with empty body ===")
try:
    resp = requests.post(webhook_url, json={}, timeout=10)
    print(f"POST Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"POST Error: {e}")

# Test POST with a sample payload (won't create real data, just test endpoint)
print("\n=== Testing POST with sample payload ===")
test_payload = {
    "event_type": "TEST",
    "trade_id": "TEST_20251201_000000_TEST",
    "direction": "Bullish",
    "entry_price": 21000.00
}
try:
    resp = requests.post(webhook_url, json=test_payload, timeout=10)
    print(f"POST Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"POST Error: {e}")

# Also check the health endpoint
print("\n=== Checking health endpoint ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/health', timeout=10)
    print(f"Health Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"Health Error: {e}")
