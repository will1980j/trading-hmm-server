import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get all unique event types
cur.execute("""
    SELECT 
        event_type,
        COUNT(*) as count,
        MIN(timestamp) as first_seen,
        MAX(timestamp) as last_seen
    FROM automated_signals
    GROUP BY event_type
    ORDER BY last_seen DESC
""")

results = cur.fetchall()

print("=" * 100)
print("ALL EVENT TYPES IN DATABASE")
print("=" * 100)

for row in results:
    event_type, count, first_seen, last_seen = row
    print(f"\nEvent Type: '{event_type}'")
    print(f"  Count: {count}")
    print(f"  First Seen: {first_seen}")
    print(f"  Last Seen: {last_seen}")

# Check the most recent 10 records
print("\n" + "=" * 100)
print("MOST RECENT 10 RECORDS")
print("=" * 100)

cur.execute("""
    SELECT 
        id,
        trade_id,
        event_type,
        direction,
        entry_price,
        signal_time,
        timestamp
    FROM automated_signals
    ORDER BY timestamp DESC
    LIMIT 10
""")

results = cur.fetchall()

for row in results:
    id, trade_id, event_type, direction, entry_price, signal_time, timestamp = row
    print(f"\nID: {id}")
    print(f"  Trade ID: {trade_id}")
    print(f"  Event Type: '{event_type}'")
    print(f"  Direction: {direction}")
    print(f"  Entry Price: {entry_price}")
    print(f"  Signal Time: {signal_time}")
    print(f"  Timestamp: {timestamp}")

cur.close()
conn.close()
