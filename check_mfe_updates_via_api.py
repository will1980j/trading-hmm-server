"""Check MFE updates via production API only - NO LOCAL DATABASE"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Get dashboard data from production API
print("=== CHECKING PRODUCTION API FOR MFE DATA ===\n")

r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
if r.status_code == 200:
    data = r.json()
    
    print("=== ACTIVE TRADES ===")
    for trade in data.get('active_trades', []):
        trade_id = trade.get('trade_id', 'unknown')
        be_mfe = trade.get('be_mfe', 'N/A')
        no_be_mfe = trade.get('no_be_mfe', 'N/A')
        event_type = trade.get('event_type', 'N/A')
        print(f"  {trade_id}: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}, event_type={event_type}")
    
    print(f"\n=== COMPLETED TRADES ===")
    for trade in data.get('completed_trades', []):
        trade_id = trade.get('trade_id', 'unknown')
        be_mfe = trade.get('be_mfe', 'N/A')
        no_be_mfe = trade.get('no_be_mfe', 'N/A')
        final_mfe = trade.get('final_mfe', 'N/A')
        print(f"  {trade_id}: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}, final_mfe={final_mfe}")
else:
    print(f"API Error: {r.status_code}")

# Check webhook stats to see if MFE_UPDATE events are being received
print("\n=== WEBHOOK STATS ===")
r2 = requests.get(f"{BASE_URL}/api/webhook-stats")
if r2.status_code == 200:
    stats = r2.json()
    print(f"Total webhooks: {stats.get('total_webhooks', 'N/A')}")
    print(f"Event types: {stats.get('event_types', {})}")
else:
    print(f"Stats API Error: {r2.status_code}")
