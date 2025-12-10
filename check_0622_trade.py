import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Find the 06:22 AM trade
cur.execute("""
    SELECT trade_id, event_type, timestamp, be_mfe, no_be_mfe, mae_global_r, raw_payload
    FROM automated_signals
    WHERE trade_id LIKE '%062200%'
    ORDER BY timestamp ASC
""")

rows = cur.fetchall()

if not rows:
    print("Trade not found - trying signal_time search...")
    cur.execute("""
        SELECT trade_id, event_type, timestamp, be_mfe, no_be_mfe, mae_global_r
        FROM automated_signals
        WHERE signal_time = '06:22:00'
        ORDER BY timestamp ASC
    """)
    rows = cur.fetchall()

print(f"Events for 06:22 AM trade:")
print("=" * 80)

for row in rows:
    trade_id, event_type, ts, be_mfe, no_be_mfe, mae, raw_payload = row
    print(f"\n{ts} - {event_type}")
    print(f"  Trade ID: {trade_id}")
    print(f"  BE MFE: {be_mfe}R, No-BE MFE: {no_be_mfe}R, MAE: {mae}R")
    
    if event_type == 'BE_TRIGGERED':
        print(f"  ⚠️ BE_TRIGGERED event found!")
        if raw_payload:
            payload = json.loads(raw_payload)
            print(f"  Payload BE MFE: {payload.get('be_mfe')}")
            print(f"  Payload No-BE MFE: {payload.get('no_be_mfe')}")

# Check max MFE achieved
if rows:
    trade_id = rows[0][0]
    cur.execute("""
        SELECT MAX(be_mfe), MAX(no_be_mfe)
        FROM automated_signals
        WHERE trade_id = %s
        AND event_type = 'MFE_UPDATE'
    """, (trade_id,))
    max_mfes = cur.fetchone()
    print(f"\n{'='*80}")
    print(f"Maximum MFE values achieved:")
    print(f"  Max BE MFE: {max_mfes[0]}R")
    print(f"  Max No-BE MFE: {max_mfes[1]}R")
    
    if max_mfes[0] and max_mfes[0] < 1.0:
        print(f"  ⚠️ BE triggered but max BE MFE was only {max_mfes[0]}R (< 1R)!")

cur.close()
conn.close()
