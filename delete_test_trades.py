#!/usr/bin/env python3
"""Delete the test trades from Railway"""
import requests

test_trades = [
    "RAILWAY_TEST_20251201_999999_BULLISH",
    "TEST_20251201_123456_BULLISH"
]

print("Deleting test trades...")

for trade_id in test_trades:
    print(f"\nDeleting: {trade_id}")
    payload = {"trade_ids": [trade_id]}
    
    try:
        resp = requests.post(
            'https://web-production-f8c3.up.railway.app/api/automated-signals/bulk-delete',
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 200:
            print(f"  ✅ Success: {resp.json()}")
        else:
            print(f"  ❌ Error {resp.status_code}: {resp.text}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")

# Verify
print("\n=== Verification ===")
resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()

remaining = [t.get('trade_id', '') for t in data.get('active_trades', []) if 'TEST' in t.get('trade_id', '') or 'RAILWAY' in t.get('trade_id', '')]
if remaining:
    print(f"❌ Still found: {remaining}")
else:
    print("✅ All test trades deleted!")

print(f"\nActive: {len(data.get('active_trades', []))}, Completed: {len(data.get('completed_trades', []))}")
