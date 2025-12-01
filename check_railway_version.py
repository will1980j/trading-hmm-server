#!/usr/bin/env python3
"""Check Railway deployment version and status"""
import requests
import json

print("=== RAILWAY DEPLOYMENT STATUS ===")

# Check health
print("\n1. Health endpoint:")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/health', timeout=30)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Check if there's a version endpoint
print("\n2. Checking for version info:")
endpoints = [
    '/api/version',
    '/api/status',
    '/api/info',
]
for ep in endpoints:
    try:
        resp = requests.get(f'https://web-production-f8c3.up.railway.app{ep}', timeout=10)
        if resp.status_code == 200:
            print(f"   {ep}: {resp.text[:200]}")
    except:
        pass

# Check the debug endpoint for any clues
print("\n3. Debug endpoint (entry count as proxy for deployment):")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/debug', timeout=30)
    data = resp.json()
    print(f"   Entry count: {data.get('entry_count')}")
    print(f"   Exit count: {data.get('exit_count')}")
except Exception as e:
    print(f"   Error: {e}")

# Try to trigger an error to see stack trace with file info
print("\n4. Checking if fallback code exists by testing parsing:")
# Send a request that would trigger the dashboard-data endpoint
# and see if signal_time is populated
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
    data = resp.json()
    
    # Find a real trade and check
    for t in data.get('active_trades', [])[:1]:
        trade_id = t.get('trade_id')
        if trade_id and not trade_id.startswith('TEST'):
            print(f"   Trade: {trade_id}")
            print(f"   signal_date in response: {t.get('signal_date')}")
            print(f"   signal_time in response: {t.get('signal_time')}")
            
            # What it SHOULD be:
            parts = trade_id.split('_')
            if len(parts) >= 2:
                date_str = parts[0]
                time_str = parts[1][:6]
                expected_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                expected_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                print(f"   EXPECTED signal_date: {expected_date}")
                print(f"   EXPECTED signal_time: {expected_time}")
except Exception as e:
    print(f"   Error: {e}")
