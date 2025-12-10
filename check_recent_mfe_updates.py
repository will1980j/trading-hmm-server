import psycopg2
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check recent MFE_UPDATE events (last 10 minutes)
cutoff = datetime.utcnow() - timedelta(minutes=10)

cur.execute("""
    SELECT trade_id, timestamp, be_mfe, no_be_mfe, raw_payload
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND timestamp > %s
    ORDER BY timestamp DESC
    LIMIT 20
""", (cutoff,))

rows = cur.fetchall()
print(f"Recent MFE_UPDATE events (last 10 minutes):")
print("=" * 80)

for row in rows:
    trade_id, ts, be_mfe, no_be_mfe, raw_payload = row
    print(f"\n{trade_id} @ {ts}")
    print(f"  DB: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}")
    
    if raw_payload:
        payload = json.loads(raw_payload)
        print(f"  Payload: be_mfe={payload.get('be_mfe')}, no_be_mfe={payload.get('no_be_mfe')}")
        print(f"  Old fields: mfe_R={payload.get('mfe_R')}, mae_R={payload.get('mae_R')}")

cur.close()
conn.close()
