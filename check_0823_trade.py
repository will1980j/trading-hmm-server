"""Check 08:23 trade status via production API"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Get the specific trade details
r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
if r.status_code == 200:
    data = r.json()
    
    # Find the 08:23 trade
    print("=== LOOKING FOR 08:23 BULLISH TRADE ===\n")
    
    # Check completed trades
    for trade in data.get('completed_trades', []):
        if '082300000' in trade.get('trade_id', ''):
            print("FOUND IN COMPLETED TRADES:")
            print(f"  trade_id: {trade.get('trade_id')}")
            print(f"  direction: {trade.get('direction')}")
            print(f"  status: {trade.get('status')}")
            print(f"  trade_status: {trade.get('trade_status')}")
            print(f"  event_type: {trade.get('event_type')}")
            print(f"  be_mfe: {trade.get('be_mfe')}")
            print(f"  no_be_mfe: {trade.get('no_be_mfe')}")
            print(f"  final_mfe: {trade.get('final_mfe')}")
            print(f"  All keys: {list(trade.keys())}")
            print()
    
    # Check active trades
    for trade in data.get('active_trades', []):
        if '082300000' in trade.get('trade_id', ''):
            print("FOUND IN ACTIVE TRADES:")
            print(f"  trade_id: {trade.get('trade_id')}")
            print(f"  direction: {trade.get('direction')}")
            print(f"  status: {trade.get('status')}")
            print(f"  trade_status: {trade.get('trade_status')}")
            print(f"  event_type: {trade.get('event_type')}")
            print(f"  be_mfe: {trade.get('be_mfe')}")
            print(f"  no_be_mfe: {trade.get('no_be_mfe')}")
            print()

# Try to get trade detail if endpoint exists
print("\n=== TRYING TRADE DETAIL ENDPOINT ===")
r2 = requests.get(f"{BASE_URL}/api/automated-signals/trade-detail/20251201_082300000_BULLISH")
if r2.status_code == 200:
    detail = r2.json()
    print(f"Trade detail response: {detail}")
else:
    print(f"Trade detail endpoint returned: {r2.status_code}")
