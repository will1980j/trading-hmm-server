import requests
import json

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

trade_id = '20251210_194500000_BEARISH'

completed = data.get('completed_trades', [])
trade = next((t for t in completed if t['trade_id'] == trade_id), None)

if trade:
    print("Raw API response for trade:")
    print(json.dumps(trade, indent=2))
else:
    print("Trade not found in API response")
