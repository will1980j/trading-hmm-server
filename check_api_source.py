import requests

# Check the dashboard data endpoint
r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print("API Response Keys:", data.keys())
print("\nActive trades count:", len(data.get('active_trades', [])))
print("Completed trades count:", len(data.get('completed_trades', [])))

print("\n--- COMPLETED TRADE DETAILS ---")
for t in data.get('completed_trades', []):
    print(f"Trade ID: {t.get('trade_id')}")
    print(f"  Event Type: {t.get('event_type')}")
    print(f"  Direction: {t.get('direction')}")
    print(f"  Entry: {t.get('entry_price')}")
    print(f"  Stop: {t.get('stop_loss')}")
    print(f"  BE MFE: {t.get('be_mfe')}")
    print(f"  No BE MFE: {t.get('no_be_mfe')}")
    print(f"  Exit Timestamp: {t.get('exit_timestamp')}")
    print()
