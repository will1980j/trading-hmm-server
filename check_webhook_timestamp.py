import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check a recent trade
cur.execute("""
    SELECT trade_id, timestamp, raw_payload 
    FROM automated_signals 
    WHERE trade_id = '20251209_215600000_BULLISH' 
    AND event_type = 'ENTRY' 
    LIMIT 1
""")

row = cur.fetchone()
if row:
    print(f"Trade ID: {row[0]}")
    print(f"DB Timestamp (UTC): {row[1]}")
    
    if row[2]:
        payload = json.loads(row[2])
        print(f"\nPayload timestamp field: {payload.get('timestamp') or payload.get('event_timestamp')}")
        print(f"\nFull payload:")
        print(json.dumps(payload, indent=2))
    else:
        print("No raw_payload stored")
else:
    print("Trade not found")

cur.close()
conn.close()
