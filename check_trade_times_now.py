import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print('=== ACTIVE TRADES ===')
for t in data.get('active_trades', [])[:3]:
    print(f"Trade ID: {t.get('trade_id')}")
    print(f"  signal_time: {t.get('signal_time')}")
    print(f"  signal_date: {t.get('signal_date')}")
    print(f"  timestamp: {t.get('timestamp')}")
    print()

print('=== COMPLETED TRADES ===')
for t in data.get('completed_trades', [])[:3]:
    print(f"Trade ID: {t.get('trade_id')}")
    print(f"  signal_time: {t.get('signal_time')}")
    print(f"  signal_date: {t.get('signal_date')}")
    print(f"  timestamp: {t.get('timestamp')}")
    print()
