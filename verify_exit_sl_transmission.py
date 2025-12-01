"""
Deep investigation: Are EXIT_SL events being transmitted and stored correctly?
"""
import requests
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

BASE_URL = "https://web-production-f8c3.up.railway.app"
DATABASE_URL = os.environ.get('DATABASE_URL')

print("=" * 80)
print("EXIT_SL TRANSMISSION VERIFICATION - DEEP DIVE")
print("=" * 80)

# Step 1: Query database directly for EXIT_SL events
print("\n1. CHECKING DATABASE FOR EXIT_SL EVENTS")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    # Count all event types
    cursor.execute("""
        SELECT event_type, COUNT(*) as count
        FROM automated_signals
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    print("\nEvent type distribution in database:")
    event_counts = {}
    for row in cursor.fetchall():
        event_type = row['event_type']
        count = row['count']
        event_counts[event_type] = count
        print(f"  {event_type}: {count}")
    
    # Check for EXIT_SL specifically
    exit_sl_count = event_counts.get('EXIT_SL', 0) + event_counts.get('EXIT_STOP_LOSS', 0)
    exit_be_count = event_counts.get('EXIT_BE', 0) + event_counts.get('EXIT_BREAK_EVEN', 0)
    entry_count = event_counts.get('ENTRY', 0)
    
    print(f"\n📊 Summary:")
    print(f"  ENTRY events: {entry_count}")
    print(f"  EXIT_BE events: {exit_be_count}")
    print(f"  EXIT_SL events: {exit_sl_count}")
    
    if exit_sl_count == 0:
        print(f"\n🚨 CRITICAL: NO EXIT_SL EVENTS IN DATABASE!")
        print(f"   This means EXIT_SL webhooks are NOT being received or stored")
    elif exit_sl_count < exit_be_count:
        print(f"\n⚠️  WARNING: More EXIT_BE ({exit_be_count}) than EXIT_SL ({exit_sl_count})")
        print(f"   Expected: EXIT_SL >= EXIT_BE (original SL should hit more often)")
    else:
        print(f"\n✅ EXIT_SL events exist in database")
    
    # Step 2: Check recent EXIT_SL events
    print("\n" + "=" * 80)
    print("2. RECENT EXIT_SL EVENTS (Last 10)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT trade_id, event_type, timestamp, signal_date, signal_time,
               entry_price, stop_loss, no_be_mfe, be_mfe
        FROM automated_signals
        WHERE event_type IN ('EXIT_SL', 'EXIT_STOP_LOSS')
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    
    exit_sl_events = cursor.fetchall()
    
    if exit_sl_events:
        print(f"\nFound {len(exit_sl_events)} recent EXIT_SL events:")
        for ev in exit_sl_events:
            print(f"\n  Trade: {ev['trade_id']}")
            print(f"    Event: {ev['event_type']}")
            print(f"    Date/Time: {ev['signal_date']} {ev['signal_time']}")
            print(f"    Timestamp: {ev['timestamp']}")
            print(f"    Entry: {ev['entry_price']}, Stop: {ev['stop_loss']}")
            print(f"    No BE MFE: {ev['no_be_mfe']}, BE MFE: {ev['be_mfe']}")
    else:
        print("\n🚨 NO EXIT_SL EVENTS FOUND IN DATABASE!")
    
    # Step 3: Check trades with EXIT_BE but no EXIT_SL
    print("\n" + "=" * 80)
    print("3. TRADES WITH EXIT_BE BUT NO EXIT_SL (Should still be ACTIVE)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT DISTINCT be.trade_id, be.timestamp as be_timestamp,
               e.signal_date, e.signal_time, e.direction
        FROM automated_signals be
        LEFT JOIN automated_signals e ON be.trade_id = e.trade_id AND e.event_type = 'ENTRY'
        WHERE be.event_type IN ('EXIT_BE', 'EXIT_BREAK_EVEN')
        AND be.trade_id NOT IN (
            SELECT trade_id FROM automated_signals 
            WHERE event_type IN ('EXIT_SL', 'EXIT_STOP_LOSS')
        )
        ORDER BY be.timestamp DESC
        LIMIT 20
    """)
    
    be_only_trades = cursor.fetchall()
    
    if be_only_trades:
        print(f"\nFound {len(be_only_trades)} trades with EXIT_BE but no EXIT_SL:")
        for trade in be_only_trades[:10]:
            print(f"\n  Trade: {trade['trade_id']}")
            print(f"    Direction: {trade['direction']}")
            print(f"    Date/Time: {trade['signal_date']} {trade['signal_time']}")
            print(f"    EXIT_BE at: {trade['be_timestamp']}")
            print(f"    ⚠️  No EXIT_SL yet - No BE strategy still ACTIVE")
        
        print(f"\n📊 These {len(be_only_trades)} trades should show as ACTIVE (No BE running)")
    else:
        print("\n✅ No trades with EXIT_BE only (all have EXIT_SL)")
    
    # Step 4: Check for trades that should have EXIT_SL but don't
    print("\n" + "=" * 80)
    print("4. CHECKING FOR MISSING EXIT_SL EVENTS")
    print("=" * 80)
    
    # Get all ENTRY events from today
    cursor.execute("""
        SELECT trade_id, signal_date, signal_time, direction, entry_price, stop_loss
        FROM automated_signals
        WHERE event_type = 'ENTRY'
        AND signal_date >= CURRENT_DATE - INTERVAL '1 day'
        ORDER BY timestamp DESC
    """)
    
    today_entries = cursor.fetchall()
    
    print(f"\nFound {len(today_entries)} ENTRY events from last 24 hours")
    
    missing_exit_sl = []
    has_exit_be_only = []
    has_exit_sl = []
    
    for entry in today_entries:
        trade_id = entry['trade_id']
        
        # Check for EXIT_SL
        cursor.execute("""
            SELECT event_type FROM automated_signals
            WHERE trade_id = %s AND event_type IN ('EXIT_SL', 'EXIT_STOP_LOSS')
        """, (trade_id,))
        exit_sl = cursor.fetchone()
        
        # Check for EXIT_BE
        cursor.execute("""
            SELECT event_type FROM automated_signals
            WHERE trade_id = %s AND event_type IN ('EXIT_BE', 'EXIT_BREAK_EVEN')
        """, (trade_id,))
        exit_be = cursor.fetchone()
        
        if exit_sl:
            has_exit_sl.append(trade_id)
        elif exit_be:
            has_exit_be_only.append(trade_id)
        else:
            missing_exit_sl.append(trade_id)
    
    print(f"\n📊 Trade Status Breakdown:")
    print(f"  Has EXIT_SL (fully completed): {len(has_exit_sl)}")
    print(f"  Has EXIT_BE only (No BE still active): {len(has_exit_be_only)}")
    print(f"  No exit events yet (both strategies active): {len(missing_exit_sl)}")
    
    if len(has_exit_be_only) > len(has_exit_sl):
        print(f"\n🚨 SUSPICIOUS: More EXIT_BE ({len(has_exit_be_only)}) than EXIT_SL ({len(has_exit_sl)})")
        print(f"   This suggests EXIT_SL webhooks may not be transmitting correctly")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n" + "=" * 80)
print("CONCLUSIONS")
print("=" * 80)

if exit_sl_count == 0:
    print("""
🚨 CRITICAL ISSUE: NO EXIT_SL EVENTS IN DATABASE

ROOT CAUSE: One of three possibilities:
1. TradingView indicator is NOT sending EXIT_SL webhooks
2. Backend is NOT receiving EXIT_SL webhooks  
3. Backend is receiving but NOT storing EXIT_SL events

NEXT STEPS:
1. Check TradingView alert log for EXIT_SL alerts
2. Check Railway logs for EXIT_SL webhook reception
3. Verify indicator code sends EXIT_SL when stop loss hit
4. Verify backend webhook handler processes EXIT_SL correctly
""")
elif len(has_exit_be_only) > 5:
    print(f"""
⚠️  POTENTIAL ISSUE: {len(has_exit_be_only)} trades with EXIT_BE but no EXIT_SL

This could be NORMAL if:
- These trades hit +1R (BE triggered) but haven't hit original SL yet
- No BE strategy is still running and hasn't been stopped out

This is ABNORMAL if:
- These trades are old (>1 hour) and should have hit SL by now
- EXIT_SL webhooks are not being sent when SL is actually hit

RECOMMENDATION:
- Monitor these trades to see if EXIT_SL eventually arrives
- Check TradingView chart to verify if SL was actually hit
- If SL hit but no EXIT_SL → indicator transmission issue
""")
else:
    print("""
✅ EXIT_SL transmission appears to be working correctly

The current active trade count may be legitimate if:
- Trades recently entered and haven't hit SL yet
- Market is trending and trades are running in profit
- No BE strategy is still active after BE=1 completed
""")
