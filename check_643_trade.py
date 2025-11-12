import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Find all events for 06:43 signal
cur.execute("""
    SELECT trade_id, event_type, signal_time, timestamp
    FROM automated_signals
    WHERE signal_time = '06:43:00'
    ORDER BY timestamp DESC
""")

rows = cur.fetchall()

print("=" * 80)
print("ALL EVENTS FOR 06:43 SIGNAL")
print("=" * 80)

if not rows:
    print("No events found for 06:43 signal")
else:
    trade_id = rows[0][0]
    print(f"Trade ID: {trade_id}")
    print(f"Total Events: {len(rows)}")
    print("\n" + "=" * 80)
    print(f"{'Event Type':<20} {'Timestamp':<30} {'Time Diff':<15}")
    print("=" * 80)
    
    first_time = rows[-1][3]  # Oldest event
    for row in reversed(rows):
        event_type = row[1]
        timestamp = row[3]
        time_diff = (timestamp - first_time).total_seconds()
        print(f"{event_type:<20} {str(timestamp):<30} +{time_diff:.1f}s")
    
    # Check if completed
    has_exit = any('EXIT' in row[1] for row in rows)
    print("\n" + "=" * 80)
    if has_exit:
        print("❌ TRADE MARKED AS COMPLETED (has EXIT event)")
        print("⚠️  This means the TradingView indicator STILL has the bug!")
        print("⚠️  You need to UPDATE the indicator code on TradingView!")
    else:
        print("✅ TRADE IS ACTIVE (no EXIT event)")

cur.close()
conn.close()
