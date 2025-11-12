import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("RECENT SIGNAL LIFECYCLE (Last 5 signals)")
print("=" * 80)

# Get last 5 unique trade_ids with ENTRY events
cur.execute("""
    SELECT DISTINCT trade_id
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY trade_id DESC
    LIMIT 5
""")

trade_ids = [row[0] for row in cur.fetchall()]

for trade_id in trade_ids:
    print(f"\n{'=' * 80}")
    print(f"Trade: {trade_id}")
    print('=' * 80)
    
    # Get all events for this trade
    cur.execute("""
        SELECT event_type, signal_time, timestamp, 
               EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) as seconds_since_last
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp
    """, (trade_id,))
    
    events = cur.fetchall()
    
    for event_type, signal_time, timestamp, seconds in events:
        duration_str = f"(+{seconds:.0f}s)" if seconds else "(start)"
        print(f"  {event_type:20s} {duration_str:10s} at {timestamp}")
    
    # Check if it has an EXIT
    has_exit = any('EXIT' in e[0] for e in events)
    if has_exit:
        print(f"\n  ❌ COMPLETED (has EXIT event)")
    else:
        print(f"\n  ✅ STILL ACTIVE (no EXIT event)")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("If all recent signals show 'COMPLETED', that means:")
print("1. Webhooks ARE working perfectly")
print("2. Signals are being created")
print("3. They're just hitting BE or SL very quickly")
print("4. Dashboard correctly shows only ACTIVE (non-exited) trades")
print("\nThe 'old' data on dashboard is actually the LAST trade that hasn't exited yet!")
