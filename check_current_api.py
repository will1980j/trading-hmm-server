import requests
resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = resp.json()
print('=== ALL TRADES ===')
for t in data.get('active_trades', []) + data.get('completed_trades', []):
    print(f"Trade: {t.get('trade_id')}")
    print(f"  Status: {t.get('status')} / {t.get('trade_status')}")
    print(f"  Event Type: {t.get('event_type')}")
    print(f"  Direction: {t.get('direction')}")
    print(f"  Entry: {t.get('entry_price')}, Stop: {t.get('stop_loss')}")
    print(f"  signal_time: {t.get('signal_time')}")
    print(f"  be_mfe: {t.get('be_mfe')}, no_be_mfe: {t.get('no_be_mfe')}")
    print()
