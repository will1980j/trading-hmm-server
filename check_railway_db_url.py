#!/usr/bin/env python3
"""Check what database the Railway server is using"""
import requests

# Call the health endpoint which might show database info
print("=== CHECKING RAILWAY HEALTH ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/health', timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")

# Check if there's a debug endpoint
print("\n=== CHECKING DATABASE DEBUG ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/debug', timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")

# Check the stats endpoint
print("\n=== CHECKING STATS ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/stats', timeout=30)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Total signals: {data.get('total_signals')}")
    print(f"Active: {data.get('active_trades')}")
    print(f"Completed: {data.get('completed_trades')}")
except Exception as e:
    print(f"Error: {e}")

# Send another test webhook and check the returned ID
print("\n=== SENDING TEST WEBHOOK ===")
test_payload = {
    "event_type": "ENTRY",
    "trade_id": "RAILWAY_TEST_20251201_999999_BULLISH",
    "direction": "Bullish",
    "entry_price": 25000.00,
    "stop_loss": 24980.00,
    "session": "TEST",
    "event_timestamp": "2025-12-01T12:00:00Z"
}
try:
    resp = requests.post('https://web-production-f8c3.up.railway.app/api/automated-signals/webhook', 
                        json=test_payload, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")
