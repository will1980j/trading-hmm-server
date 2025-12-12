import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

signal = next((s for s in data.get('active_trades', []) if '093900' in s['trade_id']), None)

if signal:
    print(f"API returns for 20251208_093900000_BEARISH:")
    print(f"  BE MFE: {signal.get('be_mfe')}R")
    print(f"  No-BE MFE: {signal.get('no_be_mfe')}R")
    print(f"  MAE: {signal.get('mae_global_r')}R")
else:
    print("Signal not found in API")
    print(f"Total active signals: {len(data.get('active_trades', []))}")
