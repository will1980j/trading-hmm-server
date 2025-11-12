import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Find most recent trade
cur.execute("""
    SELECT trade_id, event_type, signal_time, timestamp
    FROM automated_signals
    ORDER BY timestamp DESC
    LIMIT 10
""")

rows = cur.fetchall()

print("=" * 100)
print("MOST RECENT 10 EVENTS")
print("=" * 100)
print(f"{'Trade ID':<45} {'Event':<20} {'Signal Time':<12} {'Timestamp':<30}")
print("=" * 100)

for row in rows:
    print(f"{row[0]:<45} {row[1]:<20} {row[2] or 'N/A':<12} {str(row[3]):<30}")

# Group by trade_id to see complete trades
cur.execute("""
    SELECT 
        trade_id,
        signal_time,
        COUNT(*) as event_count,
        MIN(timestamp) as first_event,
        MAX(timestamp) as last_event,
        EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) as duration_seconds,
        STRING_AGG(event_type, ', ' ORDER BY timestamp) as events
    FROM automated_signals
    WHERE timestamp > NOW() - INTERVAL '1 hour'
    GROUP BY trade_id, signal_time
    ORDER BY first_event DESC
""")

trades = cur.fetchall()

print("\n" + "=" * 120)
print("RECENT TRADES (LAST HOUR)")
print("=" * 120)
print(f"{'Trade ID':<45} {'Signal':<10} {'Events':<7} {'Duration':<10} {'Event Sequence':<50}")
print("=" * 120)

for trade in trades:
    trade_id, signal_time, event_count, first_event, last_event, duration, events = trade
    status = "COMPLETED" if "EXIT" in events else "ACTIVE"
    print(f"{trade_id:<45} {signal_time or 'N/A':<10} {event_count:<7} {duration:<10.1f}s {events[:50]:<50} [{status}]")

cur.close()
conn.close()
