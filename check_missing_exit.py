import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251209_232800000_BULLISH'

# Get all events for this trade
cur.execute("""
    SELECT timestamp, event_type, be_mfe, no_be_mfe, exit_price, raw_payload
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

rows = cur.fetchall()
print(f"All events for {trade_id}:")
print("=" * 80)

for row in rows:
    ts, event_type, be_mfe, no_be_mfe, exit_price, raw_payload = row
    print(f"\n{ts} - {event_type}")
    print(f"  be_mfe={be_mfe}, no_be_mfe={no_be_mfe}, exit_price={exit_price}")
    
    if event_type in ['EXIT_SL', 'EXIT_BE', 'EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN']:
        print(f"  ⚠️ EXIT EVENT FOUND!")
        if raw_payload:
            payload = json.loads(raw_payload)
            print(f"  Payload: {json.dumps(payload, indent=2)[:500]}")

# Check if there's an exit event
cur.execute("""
    SELECT COUNT(*) 
    FROM automated_signals 
    WHERE trade_id = %s 
    AND event_type IN ('EXIT_SL', 'EXIT_BE', 'EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN')
""", (trade_id,))

exit_count = cur.fetchone()[0]
print(f"\n{'='*80}")
print(f"Exit events found: {exit_count}")

if exit_count == 0:
    print("⚠️ NO EXIT EVENT - Trade should be completed but isn't!")

cur.close()
conn.close()
