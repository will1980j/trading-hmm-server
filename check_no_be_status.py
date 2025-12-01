import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print("=== Current Dashboard State ===")
print(f"Active trades: {len(data.get('active_trades', []))}")
print(f"Completed trades: {len(data.get('completed_trades', []))}")
print()

print("ACTIVE TRADES:")
for t in data.get('active_trades', []):
    print(f"  {t.get('trade_id')} - event: {t.get('event_type')} - BE MFE: {t.get('be_mfe')}R - NO BE MFE: {t.get('no_be_mfe')}R")

print()
print("COMPLETED TRADES:")
for t in data.get('completed_trades', []):
    print(f"  {t.get('trade_id')} - event: {t.get('event_type')} - BE MFE: {t.get('be_mfe')}R - NO BE MFE: {t.get('no_be_mfe')}R")
