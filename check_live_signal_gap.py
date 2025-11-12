import psycopg2
import os
from datetime import datetime, timezone

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get the most recent ENTRY event (new signal creation)
cur.execute("""
    SELECT 
        trade_id,
        event_type,
        signal_date,
        signal_time,
        timestamp,
        EXTRACT(EPOCH FROM (NOW() - timestamp)) / 60 as minutes_ago
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 1
""")

result = cur.fetchone()

if result:
    trade_id, event_type, signal_date, signal_time, timestamp, minutes_ago = result
    print("=" * 80)
    print("LAST NEW SIGNAL (ENTRY EVENT)")
    print("=" * 80)
    print(f"Trade ID: {trade_id}")
    print(f"Signal Date: {signal_date}")
    print(f"Signal Time: {signal_time}")
    print(f"Database Timestamp: {timestamp}")
    print(f"Minutes Ago: {minutes_ago:.1f}")
    print(f"Hours Ago: {minutes_ago/60:.1f}")
    print("=" * 80)
    
    if minutes_ago > 60:
        print(f"\n⚠️ WARNING: Last new signal was {minutes_ago/60:.1f} hours ago!")
        print("This indicates the TradingView indicator is NOT sending new signals.")
else:
    print("No ENTRY events found in database!")

# Check if there are ANY recent events (not just ENTRY)
cur.execute("""
    SELECT 
        event_type,
        COUNT(*) as count,
        MAX(timestamp) as last_time,
        EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 as minutes_ago
    FROM automated_signals
    WHERE timestamp > NOW() - INTERVAL '3 hours'
    GROUP BY event_type
    ORDER BY last_time DESC
""")

results = cur.fetchall()

print("\n" + "=" * 80)
print("ALL EVENT TYPES IN LAST 3 HOURS")
print("=" * 80)
for row in results:
    event_type, count, last_time, minutes_ago = row
    print(f"{event_type:20s} - Count: {count:4d} - Last: {minutes_ago:.1f} min ago")

cur.close()
conn.close()
