import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check recent exit events
cutoff = datetime.utcnow() - timedelta(hours=2)

cur.execute("""
    SELECT trade_id, timestamp, event_type, be_mfe, no_be_mfe, exit_price
    FROM automated_signals
    WHERE event_type IN ('EXIT_SL', 'EXIT_BE', 'EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN')
    AND timestamp > %s
    ORDER BY timestamp DESC
    LIMIT 20
""", (cutoff,))

rows = cur.fetchall()
print(f"Recent EXIT events (last 2 hours):")
print("=" * 80)

if not rows:
    print("⚠️ NO EXIT EVENTS FOUND IN LAST 2 HOURS!")
else:
    for row in rows:
        trade_id, ts, event_type, be_mfe, no_be_mfe, exit_price = row
        print(f"\n{trade_id}")
        print(f"  Time: {ts}")
        print(f"  Event: {event_type}")
        print(f"  BE MFE: {be_mfe}R, No-BE MFE: {no_be_mfe}R")
        print(f"  Exit Price: {exit_price}")

# Check active trades that should be completed
print("\n" + "=" * 80)
print("Checking for trades that should be completed...")
print("=" * 80)

cur.execute("""
    SELECT 
        e.trade_id,
        e.direction,
        e.entry_price,
        e.stop_loss,
        MAX(m.timestamp) as last_mfe_update,
        MAX(m.be_mfe) as latest_be_mfe,
        MAX(m.no_be_mfe) as latest_no_be_mfe,
        COUNT(DISTINCT ex.id) as exit_count
    FROM automated_signals e
    LEFT JOIN automated_signals m ON m.trade_id = e.trade_id AND m.event_type = 'MFE_UPDATE'
    LEFT JOIN automated_signals ex ON ex.trade_id = e.trade_id AND ex.event_type LIKE 'EXIT_%'
    WHERE e.event_type = 'ENTRY'
    AND e.timestamp > %s
    GROUP BY e.trade_id, e.direction, e.entry_price, e.stop_loss
    HAVING COUNT(DISTINCT ex.id) = 0
    ORDER BY MAX(m.timestamp) ASC
    LIMIT 10
""", (cutoff,))

active_rows = cur.fetchall()
print(f"\nActive trades without EXIT events: {len(active_rows)}")

for row in active_rows:
    trade_id, direction, entry, stop, last_update, be_mfe, no_be_mfe, exit_count = row
    print(f"\n{trade_id} ({direction})")
    print(f"  Entry: {entry}, Stop: {stop}")
    print(f"  Last MFE update: {last_update}")
    print(f"  Latest BE MFE: {be_mfe}R, No-BE MFE: {no_be_mfe}R")
    print(f"  Exit events: {exit_count}")

cur.close()
conn.close()
