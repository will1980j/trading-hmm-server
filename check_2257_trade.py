import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251210_225700000_BULLISH'

# Get all MFE_UPDATE events
cur.execute("""
    SELECT timestamp, be_mfe, no_be_mfe, mae_global_r, raw_payload
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 10
""", (trade_id,))

rows = cur.fetchall()
print(f"Recent MFE_UPDATE events for {trade_id}:")
print("=" * 80)

for row in rows:
    ts, be_mfe, no_be_mfe, mae, raw_payload = row
    print(f"\n{ts}")
    print(f"  DB: BE={be_mfe}R, NoBE={no_be_mfe}R, MAE={mae}R")
    
    if raw_payload:
        payload = json.loads(raw_payload)
        print(f"  Payload: BE={payload.get('be_mfe')}, NoBE={payload.get('no_be_mfe')}")

# Check BE_TRIGGERED and EXIT_BE events
print("\n" + "=" * 80)
print("BE lifecycle events:")
cur.execute("""
    SELECT timestamp, event_type, be_mfe, no_be_mfe
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type IN ('BE_TRIGGERED', 'EXIT_BE')
    ORDER BY timestamp ASC
""", (trade_id,))

for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]}: BE={row[2]}R, NoBE={row[3]}R")

# Get entry details
print("\n" + "=" * 80)
print("Entry details:")
cur.execute("""
    SELECT entry_price, stop_loss, (entry_price - stop_loss) as risk
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type = 'ENTRY'
""", (trade_id,))

entry = cur.fetchone()
if entry:
    print(f"  Entry: {entry[0]}")
    print(f"  Stop: {entry[1]}")
    print(f"  Risk: {entry[2]} points")
    print(f"  +4R would be: {entry[0] + (4 * entry[2])}")

cur.close()
conn.close()
