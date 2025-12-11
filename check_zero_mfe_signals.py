import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

active = data.get('active_trades', [])

# Find signals with 0.00R MFE
zero_mfe = [t for t in active if t.get('be_mfe', 0) == 0 and t.get('no_be_mfe', 0) == 0]

print(f"Signals with 0.00R MFE: {len(zero_mfe)} out of {len(active)} active")
print("\nFirst 10:")
for t in zero_mfe[:10]:
    print(f"  {t['trade_id']}: Entry={t.get('entry_price')}, Stop={t.get('stop_loss')}, Session={t.get('session')}")
