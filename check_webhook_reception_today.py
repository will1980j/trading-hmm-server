#!/usr/bin/env python3
"""Check if webhooks are being received today"""
import requests

BASE_URL = 'https://web-production-f8c3.up.railway.app'

# Check webhook stats
print("=== WEBHOOK HEALTH CHECK ===")
try:
    resp = requests.get(f'{BASE_URL}/api/webhook-health', timeout=30)
    print(f"Webhook health: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Check if the webhook endpoint is accessible
print("\n=== WEBHOOK ENDPOINT TEST ===")
test_payload = {
    "event_type": "PING",
    "trade_id": "TEST_PING",
    "timestamp": "2025-12-01T00:00:00"
}
try:
    resp = requests.post(f'{BASE_URL}/api/automated-signals/webhook', json=test_payload, timeout=30)
    print(f"Webhook endpoint status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Check dashboard data endpoint
print("\n=== DASHBOARD DATA CHECK ===")
try:
    resp = requests.get(f'{BASE_URL}/api/automated-signals/dashboard-data', timeout=30)
    data = resp.json()
    print(f"Active trades: {len(data.get('active_trades', []))}")
    print(f"Completed trades: {len(data.get('completed_trades', []))}")
    if data.get('active_trades'):
        t = data['active_trades'][0]
        print(f"\nFirst active trade:")
        print(f"  trade_id: {t.get('trade_id')}")
        print(f"  timestamp: {t.get('timestamp')}")
        print(f"  signal_date: {t.get('signal_date')}")
        print(f"  signal_time: {t.get('signal_time')}")
except Exception as e:
    print(f"Error: {e}")
