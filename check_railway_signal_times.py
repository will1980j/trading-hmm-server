#!/usr/bin/env python3
"""Check signal_time data in Railway's database via API"""
import requests
import json

# Get detailed trade data
print("=== CHECKING TRADE DETAILS VIA API ===")

# Get a specific trade's details
trade_ids = [
    '20251201_001100000_BULLISH',
    '20251130_195200000_BEARISH',
    '20251130_234000000_BULLISH'
]

for trade_id in trade_ids:
    print(f"\n=== Trade: {trade_id} ===")
    try:
        # Try the trade detail endpoint
        resp = requests.get(f'https://web-production-f8c3.up.railway.app/api/automated-signals/trade/{trade_id}', timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Response: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"  Status: {resp.status_code}")
            print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

# Check the debug endpoint for more details
print("\n=== FULL DEBUG DATA ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/debug', timeout=30)
    data = resp.json()
    
    # Look at the structure of records
    if data.get('last_10_records'):
        print("Record structure (first record):")
        first_rec = data['last_10_records'][0]
        for key, value in first_rec.items():
            print(f"  {key}: {value}")
except Exception as e:
    print(f"Error: {e}")
