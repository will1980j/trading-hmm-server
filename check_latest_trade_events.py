import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("CHECKING MOST RECENT TRADE EVENTS")
print("=" * 80)

# Get the most recent trade_id
cur.execute("""
    SELECT trade_id, signal_time, entry_price, stop_loss, timestamp
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 1
""")

result = cur.fetchone()

if result:
    trade_id, signal_time, entry, sl, ts = result
    print(f"\nMost Recent Trade: {trade_id}")
    print(f"Signal Time: {signal_time}")
    print(f"Entry: {entry}")
    print(f"Stop Loss: {sl}")
    print(f"Database Timestamp: {ts}")
    
    # Get ALL events for this trade
    cur.execute("""
        SELECT 
            event_type,
            timestamp,
            EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) as seconds_since_prev
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp
    """, (trade_id,))
    
    events = cur.fetchall()
    
    print(f"\n{'=' * 80}")
    print(f"ALL EVENTS FOR THIS TRADE ({len(events)} events)")
    print('=' * 80)
    
    for event_type, event_ts, seconds in events:
        gap = f"(+{seconds:.1f}s)" if seconds else "(start)"
        print(f"{event_type:20s} {gap:12s} at {event_ts}")
    
    # Check if it has an EXIT event
    has_exit = any('EXIT' in e[0] for e in events)
    
    print(f"\n{'=' * 80}")
    if has_exit:
        print("❌ TRADE MARKED AS COMPLETED (has EXIT event)")
        print("\nThis is why it shows in 'Completed Trades' section.")
        
        # Check if the exit happened immediately
        if len(events) >= 2:
            first_event_time = events[0][1]
            last_event_time = events[-1][1]
            total_duration = (last_event_time - first_event_time).total_seconds()
            
            if total_duration < 5:
                print(f"\n⚠️ WARNING: All events happened within {total_duration:.1f} seconds!")
                print("This indicates the indicator is processing historical bars")
                print("and sending all webhooks in a single batch.")
                print("\nThe trade is NOT actually completed - it's still running on TradingView.")
    else:
        print("✅ TRADE IS ACTIVE (no EXIT event)")
        print("\nThis trade should show in 'Active Trades' section.")

cur.close()
conn.close()
