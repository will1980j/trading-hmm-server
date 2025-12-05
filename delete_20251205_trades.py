#!/usr/bin/env python3
"""Delete all trades with trade_id LIKE '20251205_00%' via production API."""

import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

# First, get the trade IDs that match the pattern
print("Fetching trades to identify matching trade_ids...")

response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
if response.status_code != 200:
    print(f"Error fetching data: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
active_trades = data.get("active_trades", [])
completed_trades = data.get("completed_trades", [])

all_trades = active_trades + completed_trades

# Find trades matching pattern '20251205_00%'
matching_trade_ids = [
    t["trade_id"] for t in all_trades 
    if t.get("trade_id", "").startswith("20251205_00")
]

print(f"Found {len(matching_trade_ids)} trades matching '20251205_00%':")
for tid in matching_trade_ids:
    print(f"  - {tid}")

if not matching_trade_ids:
    print("No matching trades found. Nothing to delete.")
    exit(0)

# Delete via bulk-delete endpoint
print(f"\nDeleting {len(matching_trade_ids)} trades...")
delete_response = requests.post(
    f"{BASE_URL}/api/automated-signals/bulk-delete",
    json={"trade_ids": matching_trade_ids}
)

if delete_response.status_code == 200:
    result = delete_response.json()
    print(f"✅ Successfully deleted {result.get('deleted_count', 0)} events")
    print(f"   Trade count: {result.get('trade_count', 0)}")
else:
    print(f"❌ Delete failed: {delete_response.status_code}")
    print(delete_response.text)
