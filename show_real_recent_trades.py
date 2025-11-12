import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("REAL RECENT TRADES (Format: YYYYMMDD_HHMMSS_DIRECTION)")
print("=" * 80)

# Get last 10 real trade_ids (not test trades)
cur.execute("""
    SELECT trade_id, MAX(timestamp) as latest
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    AND trade_id LIKE '2,025%'  -- Real trades have date format
    GROUP BY trade_id
    ORDER BY latest DESC
    LIMIT 10
""")

trade_ids = [row[0] for row in cur.fetchall()]

print(f"\nFound {len(trade_ids)} recent real trades\n")

for trade_id in trade_ids:
    # Get all events for this trade
    cur.execute("""
        SELECT event_type, timestamp
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp
    """, (trade_id,))
    
    events = cur.fetchall()
    
    # Get entry time
    entry_event = [e for e in events if e[0] == 'ENTRY'][0]
    entry_time = entry_event[1]
    
    # Check if it has an EXIT
    exit_events = [e for e in events if 'EXIT' in e[0]]
    has_exit = len(exit_events) > 0
    
    status = "❌ COMPLETED" if has_exit else "✅ ACTIVE"
    event_count = len(events)
    
    print(f"{trade_id:40s} {status:15s} Events: {event_count:2d}  Entry: {entry_time}")
    
    if has_exit:
        exit_time = exit_events[0][1]
        duration = (exit_time - entry_time).total_seconds()
        print(f"{'':40s}   Exit: {exit_events[0][0]:20s} Duration: {duration:.0f}s")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)
print("✅ ACTIVE trades = Still running, will show on dashboard")
print("❌ COMPLETED trades = Already exited, won't show as active")
