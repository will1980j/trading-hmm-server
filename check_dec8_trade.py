"""
Check the Dec 8th trade that should be stopped out
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

trade_id = "20251208_093900000_BEARISH"

print("=" * 80)
print(f"INVESTIGATING: {trade_id}")
print("=" * 80)
print()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all events for this trade
cur.execute("""
    SELECT 
        event_type,
        timestamp,
        entry_price,
        stop_loss,
        current_price,
        be_mfe,
        no_be_mfe,
        exit_price
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

events = cur.fetchall()

print(f"Total events: {len(events)}")
print()

if len(events) == 0:
    print("❌ No events found for this trade!")
    print("   This trade doesn't exist in the database.")
else:
    for i, event in enumerate(events, 1):
        print(f"Event {i}: {event[0]}")
        print(f"   Timestamp: {event[1]}")
        print(f"   Entry: ${event[2] if event[2] else 'N/A'}")
        print(f"   Stop: ${event[3] if event[3] else 'N/A'}")
        print(f"   Current Price: ${event[4] if event[4] else 'N/A'}")
        print(f"   BE MFE: {float(event[5]) if event[5] is not None else 'N/A'}")
        print(f"   No-BE MFE: {float(event[6]) if event[6] is not None else 'N/A'}")
        print(f"   Exit Price: ${event[7] if event[7] else 'N/A'}")
        print()
    
    # Check if it has EXIT event
    has_exit = any(e[0].startswith('EXIT_') for e in events)
    
    if has_exit:
        print("✅ Trade has EXIT event (completed)")
    else:
        print("⚠️ Trade has NO EXIT event (still showing as active)")
        print()
        print("   This is the problem!")
        print("   Trade from Dec 8th should have been stopped out by now.")
        print()
        
        # Check entry and stop
        entry_event = next((e for e in events if e[0] == 'ENTRY'), None)
        if entry_event:
            entry_price = float(entry_event[2]) if entry_event[2] else None
            stop_loss = float(entry_event[3]) if entry_event[3] else None
            
            if entry_price and stop_loss:
                print(f"   Entry: ${entry_price}")
                print(f"   Stop: ${stop_loss}")
                print(f"   Direction: BEARISH (SHORT)")
                print()
                print("   For a BEARISH trade:")
                print(f"   - Stop loss is ABOVE entry: ${stop_loss} > ${entry_price}")
                print(f"   - If price went above ${stop_loss}, trade should be stopped")
                print()
                print("   Possible reasons it's still active:")
                print("   1. Indicator lost tracking (restart)")
                print("   2. EXIT webhook never sent")
                print("   3. Price never hit stop (unlikely after 5 days)")
                print("   4. Indicator arrays don't go back 5 days")

# Check how old this trade is
if events:
    first_event = events[0]
    trade_age_days = (datetime.now() - first_event[1].replace(tzinfo=None)).days
    print()
    print(f"Trade Age: {trade_age_days} days old")
    print()
    
    if trade_age_days > 2:
        print("⚠️ Trade is >2 days old and still active")
        print("   Indicator typically only tracks last 500 signals")
        print("   This trade is probably too old for indicator to track")
        print()
        print("   Solution: Hybrid Sync should detect this as 'missed exit'")
        print("   and insert EXIT_SL event based on current price vs stop")

cur.close()
conn.close()

print()
print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print()
print("Old trades (>2 days) that are still 'active' should be:")
print("1. Checked if stop was hit (compare historical price to stop)")
print("2. Automatically closed with EXIT_SL event")
print("3. Or marked as 'stale' and hidden from active trades")
print()
print("The Hybrid Sync 'detect_missed_exit' function should handle this,")
print("but it needs current/historical price data to determine if stop was hit.")
