import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print("ACTIVE TRADES:")
for t in data.get('active_trades', []):
    print(f"  {t.get('trade_id')}: event_type={t.get('event_type', 'N/A')}, status={t.get('status')}")

print("\nCOMPLETED TRADES:")
for t in data.get('completed_trades', []):
    print(f"  {t.get('trade_id')}: event_type={t.get('event_type', 'N/A')}, status={t.get('status')}")
