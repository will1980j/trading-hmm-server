"""
Diagnose why trades are showing as COMPLETED with incorrect MFE of 2.95
"""
import psycopg2
import os
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/trading_platform')

def check_recent_signals():
    """Check the most recent signals and their event sequences"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("CHECKING RECENT SIGNALS - LAST 2 HOURS")
    print("="*80)
    
    # Get all events for recent signals
    cur.execute("""
        SELECT 
            trade_id,
            event_type,
            direction,
            entry_price,
            stop_loss,
            risk_distance,
            be_mfe,
            no_be_mfe,
            signal_date,
            signal_time,
            timestamp
        FROM automated_signals
        WHERE timestamp > NOW() - INTERVAL '2 hours'
        ORDER BY trade_id, timestamp
    """)
    
    results = cur.fetchall()
    
    if not results:
        print("\n❌ No signals in last 2 hours")
        return
    
    # Group by trade_id
    trades = {}
    for row in results:
        trade_id = row[0]
        if trade_id not in trades:
            trades[trade_id] = []
        trades[trade_id].append(row)
    
    print(f"\nFound {len(trades)} unique trades:")
    print("="*80)
    
    for trade_id, events in trades.items():
        print(f"\n📊 Trade ID: {trade_id}")
        print("-"*80)
        
        for event in events:
            (tid, event_type, direction, entry, stop, risk, be_mfe, no_be_mfe, 
             sig_date, sig_time, timestamp) = event
            
            print(f"\nEvent: {event_type}")
            print(f"  Time: {timestamp}")
            print(f"  Direction: {direction}")
            print(f"  Entry: {entry}, Stop: {stop}, Risk: {risk}")
            print(f"  BE MFE: {be_mfe}, No BE MFE: {no_be_mfe}")
        
        # Analyze the event sequence
        event_types = [e[1] for e in events]
        print(f"\n📋 Event Sequence: {' → '.join(event_types)}")
        
        # Check for issues
        if len(events) == 1 and events[0][1] == 'ENTRY':
            print("✓ Normal: Only ENTRY event (trade just started)")
        elif 'EXIT_STOP_LOSS' in event_types or 'EXIT_BREAK_EVEN' in event_types:
            print("⚠️  ISSUE: Trade marked as COMPLETED immediately after ENTRY")
            print("   This suggests EXIT event is being sent too early")
        elif all(e[6] == e[7] for e in events if e[6] is not None):  # be_mfe == no_be_mfe
            print("⚠️  ISSUE: BE MFE and No BE MFE are identical")
            print("   This suggests MFE tracking isn't working correctly")
        
        # Check MFE value of 2.95
        for event in events:
            if event[6] == 2.95 or event[7] == 2.95:
                print(f"⚠️  ISSUE: MFE value is exactly 2.95")
                print(f"   Entry: {event[3]}, Stop: {event[4]}, Risk: {event[5]}")
                if event[5]:
                    calculated_mfe = 2.95 * float(event[5])
                    print(f"   If MFE=2.95R, price moved: {calculated_mfe} points")
    
    # Check for ENTRY events without subsequent MFE_UPDATE
    print("\n" + "="*80)
    print("CHECKING FOR MISSING MFE_UPDATE EVENTS")
    print("="*80)
    
    cur.execute("""
        WITH entry_events AS (
            SELECT DISTINCT trade_id, timestamp as entry_time
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND timestamp > NOW() - INTERVAL '2 hours'
        ),
        mfe_events AS (
            SELECT DISTINCT trade_id
            FROM automated_signals
            WHERE event_type = 'MFE_UPDATE'
            AND timestamp > NOW() - INTERVAL '2 hours'
        )
        SELECT e.trade_id, e.entry_time
        FROM entry_events e
        LEFT JOIN mfe_events m ON e.trade_id = m.trade_id
        WHERE m.trade_id IS NULL
    """)
    
    missing_mfe = cur.fetchall()
    
    if missing_mfe:
        print(f"\n⚠️  Found {len(missing_mfe)} trades with ENTRY but no MFE_UPDATE:")
        for trade_id, entry_time in missing_mfe:
            time_since = datetime.now() - entry_time.replace(tzinfo=None)
            print(f"  - {trade_id} (entered {time_since} ago)")
        print("\nThis suggests MFE_UPDATE webhooks aren't being sent")
    else:
        print("\n✓ All ENTRY events have corresponding MFE_UPDATE events")
    
    cur.close()
    conn.close()

def check_indicator_logic():
    """Check what the indicator should be sending"""
    print("\n" + "="*80)
    print("INDICATOR WEBHOOK LOGIC CHECK")
    print("="*80)
    
    print("""
Expected Webhook Sequence:

1. ENTRY (signal_created):
   - Sent when confirmation happens
   - Contains: entry_price, stop_loss, risk_distance
   - MFE values: be_mfe=0.0, no_be_mfe=0.0
   - Status: "active"

2. MFE_UPDATE (mfe_update):
   - Sent EVERY BAR while trade is active
   - Contains: updated be_mfe and no_be_mfe values
   - Should continue until EXIT event

3. BE_TRIGGERED (be_triggered):
   - Sent when price reaches +1R (BE=1 strategy)
   - Contains: be_mfe at trigger point
   - Only for BE=1 strategy

4. EXIT_STOP_LOSS or EXIT_BREAK_EVEN (signal_completed):
   - Sent when trade resolves
   - Contains: final MFE values
   - Status: "completed"

Current Issue:
- Trades showing as COMPLETED immediately
- MFE stuck at 2.95 for both BE and No BE
- Suggests EXIT event is being sent too early
- OR dashboard is misinterpreting ENTRY as EXIT
""")

if __name__ == "__main__":
    check_recent_signals()
    check_indicator_logic()
