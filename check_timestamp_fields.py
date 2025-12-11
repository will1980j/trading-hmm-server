import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

trade_id = '20251210_194500000_BEARISH'

completed = data.get('completed_trades', [])
trade = next((t for t in completed if t['trade_id'] == trade_id), None)

if trade:
    print(f"Timestamp fields for {trade_id}:")
    print(f"  entry_ts: {trade.get('entry_ts')}")
    print(f"  exit_ts: {trade.get('exit_ts')}")
    print(f"  event_ts: {trade.get('event_ts')}")
    print(f"  timestamp: {trade.get('timestamp')}")
    
    if not trade.get('entry_ts'):
        print("\n  PROBLEM: entry_ts is missing!")
    if not trade.get('exit_ts') and not trade.get('timestamp'):
        print("\n  PROBLEM: exit_ts/timestamp is missing!")
else:
    print("Trade not found")
