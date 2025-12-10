import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check a recent active trade
trade_id = '20251209_234000000_BEARISH'

cur.execute("""
    SELECT timestamp, be_mfe, no_be_mfe, raw_payload
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND trade_id = %s
    ORDER BY timestamp DESC
    LIMIT 5
""", (trade_id,))

rows = cur.fetchall()
print(f"MFE_UPDATE events for {trade_id}:")
print("=" * 80)

for row in rows:
    ts, be_mfe, no_be_mfe, raw_payload = row
    print(f"\nTimestamp: {ts}")
    print(f"  DB be_mfe: {be_mfe}")
    print(f"  DB no_be_mfe: {no_be_mfe}")
    
    if raw_payload:
        payload = json.loads(raw_payload)
        print(f"  Payload be_mfe: {payload.get('be_mfe')}")
        print(f"  Payload no_be_mfe: {payload.get('no_be_mfe')}")
        print(f"  Payload mfe_R: {payload.get('mfe_R')}")
        print(f"  Payload mae_R: {payload.get('mae_R')}")

cur.close()
conn.close()
