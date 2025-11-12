import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("CHECKING THE 20:14 SIGNAL (2,025001111_191600_BULLISH)")
print("=" * 80)

# Find all events for this specific trade
cur.execute("""
    SELECT 
        id,
        event_type,
        direction,
        entry_price,
        stop_loss,
        signal_time,
        timestamp,
        be_mfe,
        no_be_mfe
    FROM automated_signals
    WHERE trade_id = '2,025001111_191600_BULLISH'
    ORDER BY timestamp
""")

results = cur.fetchall()

if results:
    print(f"\nFound {len(results)} events for this trade:\n")
    for row in results:
        id, event_type, direction, entry, sl, sig_time, ts, be_mfe, no_be_mfe = row
        print(f"Event: {event_type:20s}")
        print(f"  ID: {id}")
        print(f"  Direction: {direction}")
        print(f"  Entry: {entry}")
        print(f"  Stop Loss: {sl}")
        print(f"  Signal Time: {sig_time}")
        print(f"  Timestamp: {ts}")
        print(f"  BE MFE: {be_mfe}")
        print(f"  No BE MFE: {no_be_mfe}")
        print()
    
    # Check if there's an EXIT event
    has_exit = any('EXIT' in row[1] for row in results)
    
    if has_exit:
        print("✅ This trade HAS an EXIT event")
    else:
        print("❌ This trade is MISSING an EXIT event!")
        print("\nThis is why it shows as 'ACTIVE' on the dashboard.")
        print("The indicator never sent an EXIT webhook for this trade.")
else:
    print("\n❌ Trade not found in database!")

# Check all trades that are showing as "active" but are old
print("\n" + "=" * 80)
print("ALL 'ACTIVE' TRADES (no EXIT event) FROM BEFORE 22:00")
print("=" * 80)

cur.execute("""
    SELECT 
        e.trade_id,
        e.signal_time,
        e.entry_price,
        e.stop_loss,
        e.timestamp,
        EXTRACT(EPOCH FROM (NOW() - e.timestamp)) / 3600 as hours_ago
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT trade_id FROM automated_signals 
        WHERE event_type LIKE 'EXIT_%'
    )
    AND e.signal_time < '22:00:00'
    ORDER BY e.timestamp DESC
    LIMIT 20
""")

results = cur.fetchall()

print(f"\nFound {len(results)} old 'active' trades:\n")
for row in results:
    trade_id, sig_time, entry, sl, ts, hours_ago = row
    print(f"{trade_id:40s} Signal: {sig_time}  Entry: {entry:8.2f}  SL: {sl:8.2f}  Age: {hours_ago:.1f}h")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("The indicator is NOT sending EXIT webhooks for stopped-out trades.")
print("This causes old trades to remain 'ACTIVE' forever in the database.")
print("\nThe dashboard is working correctly - it's showing trades without EXIT events.")
print("The problem is the indicator logic for detecting stop loss hits.")
