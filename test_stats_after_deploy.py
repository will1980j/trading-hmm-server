import requests
import json
import time

print("=== TESTING STATS AFTER DEPLOYMENT ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Waiting for deployment...")
print("Press Enter after pushing and waiting 2-3 minutes...")
input()

print("\n1. Checking debug endpoint...")
debug_url = f'{base_url}/api/automated-signals/debug'
try:
    response = requests.get(debug_url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"Total in DB (from debug): {data.get('total_in_db', 0)}")
except Exception as e:
    print(f"Error: {e}")

print("\n2. Checking stats endpoint...")
stats_url = f'{base_url}/api/automated-signals/stats'
try:
    response = requests.get(stats_url, timeout=10)
    if response.status_code == 200:
        stats = response.json()
        print(f"Stats response:")
        print(json.dumps(stats, indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n3. Sending a new ENTRY signal...")
webhook_url = f'{base_url}/api/automated-signals'

test_signal = {
    "type": "signal_created",
    "signal_id": "STATS_TEST_001",
    "date": "2024-11-11",
    "time": "13:45:00",
    "bias": "Bearish",
    "session": "NY PM",
    "entry_price": 21000.00,
    "sl_price": 21025.00,
    "risk_distance": 25.00,
    "be_price": 21000.00,
    "target_1r": 20975.00,
    "target_2r": 20950.00,
    "target_3r": 20925.00,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1731341100000
}

try:
    response = requests.post(webhook_url, json=test_signal, timeout=10)
    print(f"Webhook status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Signal ID: {result.get('signal_id')}")
        
        # Wait and check stats again
        time.sleep(2)
        print("\n4. Checking stats again after new signal...")
        stats_response = requests.get(stats_url, timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"Total signals: {stats.get('stats', {}).get('total_signals', 0)}")
            print(f"Active: {stats.get('stats', {}).get('active_count', 0)}")
except Exception as e:
    print(f"Error: {e}")

print("\n5. Check Railway logs for the stats query log messages")
print("Look for: '📊 Stats: Raw count from database'")
print("This will tell us what the database actually returns")
