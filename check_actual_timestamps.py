import psycopg2
import os
from datetime import datetime, timezone

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get the 5 most recent signals with ALL timestamp fields
cur.execute("""
    SELECT 
        trade_id,
        event_type,
        direction,
        signal_date,
        signal_time,
        timestamp,
        NOW() as current_db_time,
        EXTRACT(EPOCH FROM (NOW() - timestamp)) / 60 as minutes_ago
    FROM automated_signals
    ORDER BY id DESC
    LIMIT 5
""")

results = cur.fetchall()

print("=" * 100)
print("RECENT SIGNALS WITH FULL TIMESTAMP DATA")
print("=" * 100)

for row in results:
    trade_id, event_type, direction, signal_date, signal_time, timestamp, db_now, minutes_ago = row
    print(f"\nTrade ID: {trade_id}")
    print(f"Event: {event_type}")
    print(f"Direction: {direction}")
    print(f"Signal Date: {signal_date}")
    print(f"Signal Time: {signal_time}")
    print(f"Timestamp (DB): {timestamp}")
    print(f"Current DB Time: {db_now}")
    print(f"Minutes Ago: {minutes_ago:.1f}")
    print("-" * 100)

cur.close()
conn.close()
