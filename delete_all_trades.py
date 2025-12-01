#!/usr/bin/env python3
"""Delete ALL trades from the automated_signals table to start fresh"""
import requests

# First get all trade IDs
print("Fetching all trades...")
resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()

active = data.get('active_trades', [])
completed = data.get('completed_trades', [])

all_trade_ids = []
for t in active:
    tid = t.get('trade_id', '')
    if tid and tid not in all_trade_ids:
        all_trade_ids.append(tid)

for t in completed:
    tid = t.get('trade_id', '')
    if tid and tid not in all_trade_ids:
        all_trade_ids.append(tid)

print(f"Found {len(all_trade_ids)} unique trades to delete")

if len(all_trade_ids) == 0:
    print("No trades to delete!")
    exit(0)

# Delete in batches of 10
batch_size = 10
deleted = 0

for i in range(0, len(all_trade_ids), batch_size):
    batch = all_trade_ids[i:i+batch_size]
    print(f"\nDeleting batch {i//batch_size + 1}: {len(batch)} trades...")
    
    payload = {"trade_ids": batch}
    try:
        resp = requests.post(
            'https://web-production-f8c3.up.railway.app/api/automated-signals/bulk-delete',
            json=payload,
            timeout=60
        )
        
        if resp.status_code == 200:
            result = resp.json()
            deleted += result.get('deleted_count', 0)
            print(f"  ✅ Deleted {result.get('deleted_count', 0)} trades")
        else:
            print(f"  ❌ Error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print(f"\n{'='*60}")
print(f"TOTAL DELETED: {deleted} trades")

# Verify
print("\nVerifying...")
resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()
remaining_active = len(data.get('active_trades', []))
remaining_completed = len(data.get('completed_trades', []))

if remaining_active == 0 and remaining_completed == 0:
    print("✅ All trades deleted! Database is clean.")
else:
    print(f"⚠️ Still have {remaining_active} active, {remaining_completed} completed")
