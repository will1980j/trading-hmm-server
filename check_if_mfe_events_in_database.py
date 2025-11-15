"""
Check if MFE_UPDATE events are actually in the automated_signals table
"""

import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

# Pick a specific signal_id from the alert log
signal_id = "20251114_000200000_BEARISH"

print(f"Checking database for signal_id: {signal_id}")
print("=" * 80)

# Get trade detail
response = requests.get(f"{BASE_URL}/api/automated-signals/trade-detail/{signal_id}")
data = response.json()

if data.get('success'):
    trade = data.get('trade', {})
    events = trade.get('events', [])
    
    print(f"\nTotal events in database: {len(events)}")
    print("\nEvent types:")
    for event in events:
        print(f"  - {event.get('event_type')}: BE MFE={event.get('be_mfe')}, No BE MFE={event.get('no_be_mfe')}")
    
    if len(events) == 1:
        print("\n⚠️  PROBLEM FOUND: Only 1 event (ENTRY) in database!")
        print("The MFE_UPDATE events from TradingView are NOT being stored!")
    else:
        print(f"\n✅ Good: {len(events)} events found")
else:
    print(f"ERROR: {data.get('error')}")
