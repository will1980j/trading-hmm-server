"""
Test if a specific active trade has MFE updates in the database
"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Get an active trade ID
resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=10)
data = resp.json()
active = data.get('active_trades', [])

if active:
    trade_id = active[0]['trade_id']
    print(f"Testing trade: {trade_id}")
    print(f"Current MFE values from dashboard:")
    print(f"  BE MFE: {active[0].get('be_mfe')}R")
    print(f"  No BE MFE: {active[0].get('no_be_mfe')}R")
    
    # Get trade detail to see all events
    resp2 = requests.get(f"{BASE_URL}/api/automated-signals/trade/{trade_id}", timeout=10)
    detail = resp2.json()
    
    if detail.get('events'):
        print(f"\nEvents for this trade:")
        for ev in detail['events']:
            print(f"  {ev.get('event_type')}: MFE={ev.get('mfe') or ev.get('no_be_mfe') or 'N/A'}R")
        
        mfe_update_count = sum(1 for ev in detail['events'] if ev.get('event_type') == 'MFE_UPDATE')
        print(f"\nMFE_UPDATE events: {mfe_update_count}")
        
        if mfe_update_count == 0:
            print("🚨 NO MFE_UPDATE events found - webhooks not being received or stored")
        else:
            print("✅ MFE_UPDATE events exist but not showing on ENTRY row")
else:
    print("No active trades")
