"""
Check all events for the new bearish trade via API
"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("CHECKING NEW BEARISH TRADE EVENTS")
print("=" * 80)

# Get dashboard data
r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = r.json()

print(f"\nActive trades: {len(data.get('active_trades', []))}")

if data.get('active_trades'):
    trade = data['active_trades'][0]
    print(f"\nTrade details:")
    print(f"  Trade ID: {trade['trade_id']}")
    print(f"  Direction: {trade['direction']}")
    print(f"  Entry: {trade['entry_price']}")
    print(f"  Stop: {trade['stop_loss']}")
    print(f"  BE MFE: {trade['be_mfe']}")
    print(f"  No BE MFE: {trade['no_be_mfe']}")
    print(f"  Current Price: {trade.get('current_price')}")
    print(f"  Time: {trade.get('signal_time')}")
    
    # The chart shows MFE values but dashboard shows 0.00
    # This means either:
    # 1. MFE_UPDATE webhooks aren't arriving
    # 2. MFE_UPDATE webhooks are arriving but not being stored
    # 3. The query isn't finding the MFE_UPDATE rows
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    if trade['be_mfe'] == 0.0 and trade['no_be_mfe'] == 0.0:
        print("❌ MFE VALUES ARE STILL 0.00")
        print("\nPossible causes:")
        print("1. MFE_UPDATE webhooks not being sent by indicator")
        print("2. MFE_UPDATE webhooks being sent but not stored in database")
        print("3. Database query not finding MFE_UPDATE rows")
        print("4. Railway deployment not complete yet")
    else:
        print("✅ MFE VALUES ARE WORKING!")
        print(f"   BE MFE: {trade['be_mfe']}R")
        print(f"   No BE MFE: {trade['no_be_mfe']}R")
else:
    print("\n❌ NO ACTIVE TRADES FOUND")

print("=" * 80)
