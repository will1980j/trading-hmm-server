import requests
import json

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("CHECKING LIVE DASHBOARD DATA")
print("=" * 80)

# Get dashboard data
response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = response.json()

print(f"\nActive Trades: {len(data['active_trades'])}")
print(f"Completed Trades: {len(data['completed_trades'])}")

print("\n" + "=" * 80)
print("ACTIVE TRADES - MFE VALUES")
print("=" * 80)

for trade in data['active_trades'][:10]:  # First 10
    trade_id = trade['trade_id']
    be_mfe = trade.get('be_mfe', 'MISSING')
    no_be_mfe = trade.get('no_be_mfe', 'MISSING')
    direction = trade['direction']
    
    print(f"\n{trade_id}")
    print(f"  Direction: {direction}")
    print(f"  BE_MFE: {be_mfe}")
    print(f"  NO_BE_MFE: {no_be_mfe}")
    print(f"  Status: {trade.get('status', 'UNKNOWN')}")

print("\n" + "=" * 80)
print("COMPLETED TRADES - CHECKING IF THEY SHOULD BE ACTIVE")
print("=" * 80)

# Check a few completed trades to see why they're marked complete
for trade in data['completed_trades'][:5]:
    trade_id = trade['trade_id']
    status = trade.get('status', 'UNKNOWN')
    be_mfe = trade.get('be_mfe', 'MISSING')
    no_be_mfe = trade.get('no_be_mfe', 'MISSING')
    
    print(f"\n{trade_id}")
    print(f"  Status: {status}")
    print(f"  BE_MFE: {be_mfe}")
    print(f"  NO_BE_MFE: {no_be_mfe}")
    print(f"  Direction: {trade['direction']}")
    print(f"  Entry: {trade.get('entry_price', 'N/A')}")

print("\n" + "=" * 80)
print("CHECKING RAW DATABASE EVENTS FOR ONE TRADE")
print("=" * 80)

# Pick one trade and check all its events
if data['active_trades']:
    sample_trade_id = data['active_trades'][0]['trade_id']
    print(f"\nSample Trade: {sample_trade_id}")
    
    # This would require direct database access
    # Let's check via the stats endpoint instead
    stats_response = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
    stats = stats_response.json()
    
    print(f"\nOverall Stats:")
    print(f"  Total Active: {stats.get('active_count', 'N/A')}")
    print(f"  Total Completed: {stats.get('completed_count', 'N/A')}")
    print(f"  Win Rate: {stats.get('win_rate', 'N/A')}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
