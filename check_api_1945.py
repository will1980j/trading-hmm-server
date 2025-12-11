import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

trade_id = '20251210_194500000_BEARISH'

all_trades = data.get('active_trades', []) + data.get('completed_trades', [])
trade = next((t for t in all_trades if t['trade_id'] == trade_id), None)

if trade:
    print(f"Trade: {trade_id}")
    print(f"BE MFE: {trade.get('be_mfe')}R")
    print(f"No-BE MFE: {trade.get('no_be_mfe')}R")
    print(f"MAE: {trade.get('mae_global_r')}R")
    
    if trade.get('be_mfe') == trade.get('no_be_mfe'):
        print("\nPROBLEM: Both MFE values are identical!")
        print("Expected: BE=1.16R (frozen), No-BE=2.29R (latest)")
else:
    print("Trade not found")
