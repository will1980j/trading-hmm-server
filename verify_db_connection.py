#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')

# Parse the URL to show host/port (hide password)
if db_url:
    # Format: postgresql://user:pass@host:port/dbname
    parts = db_url.split('@')
    if len(parts) > 1:
        host_part = parts[1]
        print(f"Connecting to: {host_part}")
    else:
        print("Could not parse DATABASE_URL")
else:
    print("DATABASE_URL not set!")

# Now let's query the Railway API to see what database it's using
import requests
resp = requests.get("https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data")
data = resp.json()

print(f"\nRailway API returns:")
print(f"  Active: {len(data.get('active_trades', []))}")
print(f"  Completed: {len(data.get('completed_trades', []))}")

# Show the actual trade data
for t in data.get('active_trades', []) + data.get('completed_trades', []):
    print(f"\n  Trade: {t.get('trade_id')}")
    print(f"    Direction: {t.get('direction')}")
    print(f"    signal_time: {t.get('signal_time')}")
    print(f"    signal_date: {t.get('signal_date')}")
    print(f"    entry: {t.get('entry_price')}, stop: {t.get('stop_loss')}")
    print(f"    be_mfe: {t.get('be_mfe')}, no_be_mfe: {t.get('no_be_mfe')}")
    print(f"    status: {t.get('status')}")
    print(f"    age: {t.get('age')}")
