"""
Diagnose why dashboard shows no signals and journey map is empty
"""

import requests
import json

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("DASHBOARD EMPTY ISSUE DIAGNOSTIC")
print("=" * 80)

# 1. Check dashboard-data endpoint
print("\n1. Checking dashboard-data endpoint:")
print("-" * 80)

response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = response.json()

print(f"Status Code: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Active Trades: {len(data.get('active_trades', []))}")
print(f"Completed Trades: {len(data.get('completed_trades', []))}")

if data.get('active_trades'):
    print("\nFirst Active Trade:")
    print(json.dumps(data['active_trades'][0], indent=2))

if data.get('completed_trades'):
    print("\nFirst Completed Trade:")
    print(json.dumps(data['completed_trades'][0], indent=2))

# 2. Check if there's an error
if 'error' in data:
    print(f"\nERROR: {data['error']}")

# 3. Try to get a specific trade detail
print("\n\n2. Trying to get trade detail for a specific trade:")
print("-" * 80)

# First, let's see if we can find any trade_id
if data.get('active_trades') or data.get('completed_trades'):
    all_trades = (data.get('active_trades', []) + data.get('completed_trades', []))
    if all_trades:
        trade_id = all_trades[0].get('trade_id')
        print(f"Testing with trade_id: {trade_id}")
        
        detail_response = requests.get(f"{BASE_URL}/api/automated-signals/trade-detail/{trade_id}")
        detail_data = detail_response.json()
        
        print(f"Status Code: {detail_response.status_code}")
        print(f"Success: {detail_data.get('success')}")
        
        if detail_data.get('success'):
            trade = detail_data.get('trade', {})
            print(f"Trade has {len(trade.get('events', []))} events")
            print("\nEvents:")
            for event in trade.get('events', []):
                print(f"  - {event.get('event_type')}: BE MFE={event.get('be_mfe')}, No BE MFE={event.get('no_be_mfe')}")
        else:
            print(f"ERROR: {detail_data.get('error')}")
else:
    print("No trades found to test with!")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
