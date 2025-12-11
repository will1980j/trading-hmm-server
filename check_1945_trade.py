import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251210_194500000_BEARISH'

# Get all events for this trade
cur.execute("""
    SELECT timestamp, event_type, be_mfe, no_be_mfe, mae_global_r, raw_payload
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

rows = cur.fetchall()
print(f"All events for {trade_id}:")
print("=" * 80)

for row in rows:
    ts, event_type, be_mfe, no_be_mfe, mae, raw_payload = row
    print(f"\n{ts} - {event_type}")
    print(f"  BE MFE: {be_mfe}R")
    print(f"  No-BE MFE: {no_be_mfe}R")
    print(f"  MAE: {mae}R")
    
    if event_type == 'BE_TRIGGERED':
        print(f"  ⚠️ BE TRIGGERED at this point")
    
    if event_type == 'EXIT_BE':
        print(f"  ⚠️ BE=1 strategy exited (hit entry after BE trigger)")
    
    if raw_payload and event_type == 'MFE_UPDATE':
        payload = json.loads(raw_payload)
        print(f"  Payload: be_mfe={payload.get('be_mfe')}, no_be_mfe={payload.get('no_be_mfe')}")

# Check what the dashboard API returns
print("\n" + "=" * 80)
print("Dashboard API data:")
import requests
r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

all_trades = data.get('active_trades', []) + data.get('completed_trades', [])
trade = next((t for t in all_trades if t['trade_id'] == trade_id), None)

if trade:
    print(f"  BE Status: {trade.get('be_status')}")
    print(f"  No-BE Status: {trade.get('no_be_status')}")
    print(f"  BE MFE: {trade.get('be_mfe')}R")
    print(f"  No-BE MFE: {trade.get('no_be_mfe')}R")
    print(f"  MAE: {trade.get('mae_global_r')}R")
else:
    print("  Trade not found in dashboard API")

cur.close()
conn.close()
