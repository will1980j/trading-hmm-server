import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

active = data.get('active_trades', [])
print(f"Active signals in API: {len(active)}")
print()

if active:
    print("First 5 signals:")
    for s in active[:5]:
        print(f"  {s['trade_id']}: BE={s.get('be_mfe')}R, NoBE={s.get('no_be_mfe')}R, MAE={s.get('mae_global_r')}R")
else:
    print("No active signals in API")
