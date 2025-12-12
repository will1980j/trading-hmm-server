"""Check if dashboard API is showing the updated signals"""

import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

active = data.get('active_trades', [])
print(f"Active signals in dashboard API: {len(active)}")
print()

# Check one of the 14 signals that should be updating
test_signal = next((s for s in active if '201100' in s['trade_id']), None)
if test_signal:
    print(f"Signal 20251211_201100000_BULLISH:")
    print(f"  BE MFE: {test_signal.get('be_mfe')}R")
    print(f"  No-BE MFE: {test_signal.get('no_be_mfe')}R")
    print(f"  MAE: {test_signal.get('mae_global_r')}R")
    print(f"  Timestamp: {test_signal.get('timestamp')}")
else:
    print("Signal not found in API response")
