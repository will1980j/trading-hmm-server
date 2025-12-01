import requests
import time

print("Checking if signal_time changes between API calls...")
print()

for i in range(3):
    r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
    data = r.json()
    
    print(f"=== Call {i+1} at {time.strftime('%H:%M:%S')} ===")
    for t in data.get('active_trades', [])[:2]:
        print(f"  Trade: {t.get('trade_id')}")
        print(f"    signal_time: {t.get('signal_time')}")
        print(f"    timestamp: {t.get('timestamp')}")
    print()
    
    if i < 2:
        print("Waiting 5 seconds...")
        time.sleep(5)

print("If signal_time stays the same, the bug is in the JavaScript rendering.")
print("If signal_time changes, the bug is in the backend.")
