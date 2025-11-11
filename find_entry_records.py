import requests
import json

print("=== FINDING ENTRY RECORDS ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

# Send a fresh ENTRY signal
webhook_url = f'{base_url}/api/automated-signals'

test_signal = {
    "type": "signal_created",
    "signal_id": "FIND_ME_12345",
    "date": "2024-11-11",
    "time": "13:30:00",
    "bias": "Bullish",
    "session": "NY PM",
    "entry_price": 21050.00,
    "sl_price": 21025.00,
    "risk_distance": 25.00,
    "be_price": 21050.00,
    "target_1r": 21075.00,
    "target_2r": 21100.00,
    "target_3r": 21125.00,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1731340800000
}

print("1. Sending ENTRY signal...")
try:
    response = requests.post(webhook_url, json=test_signal, timeout=10)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        db_id = result.get('signal_id')
        print(f"\n✓ ENTRY saved with ID: {db_id}")
        
        # Now check if it's in the database
        print("\n2. Checking debug endpoint for this record...")
        debug_url = f'{base_url}/api/automated-signals/debug'
        debug_response = requests.get(debug_url, timeout=10)
        
        if debug_response.status_code == 200:
            data = debug_response.json()
            records = data.get('last_10_records', [])
            
            # Look for our record
            found = False
            for record in records:
                if record.get('trade_id') == 'FIND_ME_12345':
                    print(f"\n✓ FOUND IT!")
                    print(json.dumps(record, indent=2))
                    found = True
                    break
                elif record.get('id') == db_id:
                    print(f"\n✓ FOUND BY ID!")
                    print(json.dumps(record, indent=2))
                    found = True
                    break
            
            if not found:
                print(f"\n✗ NOT FOUND in last 10 records")
                print("\nLast 10 records:")
                for r in records:
                    print(f"  ID {r.get('id')}: {r.get('event_type')} - {r.get('trade_id')}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n3. Checking stats...")
stats_url = f'{base_url}/api/automated-signals/stats'
try:
    response = requests.get(stats_url, timeout=10)
    if response.status_code == 200:
        stats = response.json()
        print(f"Total signals: {stats.get('stats', {}).get('total_signals', 0)}")
        print(f"Active: {stats.get('stats', {}).get('active_count', 0)}")
except Exception as e:
    print(f"Error: {e}")
