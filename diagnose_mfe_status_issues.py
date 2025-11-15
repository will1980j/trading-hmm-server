import psycopg2
from datetime import datetime
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("DIAGNOSING MFE AND STATUS ISSUES")
print("=" * 80)

# Get all unique trade_ids
cur.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    ORDER BY trade_id DESC 
    LIMIT 10
""")
trade_ids = [row[0] for row in cur.fetchall()]

print(f"\nAnalyzing {len(trade_ids)} most recent trades...\n")

for trade_id in trade_ids:
    print(f"\n{'='*80}")
    print(f"TRADE: {trade_id}")
    print(f"{'='*80}")
    
    # Get all events for this trade
    cur.execute("""
        SELECT event_type, be_mfe, no_be_mfe, entry_price, stop_loss, 
               signal_time, timestamp
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp
    """, (trade_id,))
    
    events = cur.fetchall()
    
    print(f"\nTotal Events: {len(events)}")
    
    for i, event in enumerate(events, 1):
        event_type, be_mfe, no_be_mfe, entry, sl, sig_time, ts = event
        print(f"\n  Event {i}: {event_type}")
        print(f"    BE MFE: {be_mfe}")
        print(f"    No BE MFE: {no_be_mfe}")
        print(f"    Entry: {entry}")
        print(f"    Stop Loss: {sl}")
        print(f"    Time: {sig_time or ts}")
        
        # Check for issues
        if be_mfe == no_be_mfe and be_mfe is not None:
            print(f"    ⚠️  WARNING: BE MFE equals No BE MFE ({be_mfe})")
        
        if event_type.startswith('EXIT_'):
            print(f"    ✓ Trade marked as COMPLETED")
        
    # Determine if trade should actually be active
    latest_event = events[-1]
    latest_event_type = latest_event[0]
    latest_be_mfe = latest_event[1]
    latest_no_be_mfe = latest_event[2]
    
    print(f"\n  ANALYSIS:")
    print(f"    Latest Event Type: {latest_event_type}")
    print(f"    Dashboard Status: {'COMPLETED' if latest_event_type.startswith('EXIT_') else 'ACTIVE'}")
    
    if latest_event_type.startswith('EXIT_'):
        print(f"    ✓ Correctly marked as COMPLETED")
    else:
        print(f"    ✓ Should be ACTIVE")
        
        # Check if No BE MFE suggests trade should still be running
        if latest_no_be_mfe and latest_no_be_mfe > 0:
            print(f"    ✓ No BE MFE = {latest_no_be_mfe}R (trade still running)")
        
        # Check if BE MFE suggests BE was triggered
        if latest_be_mfe and latest_be_mfe >= 1.0:
            print(f"    ⚠️  BE MFE = {latest_be_mfe}R (BE should have triggered)")

print("\n" + "="*80)
print("CHECKING INDICATOR LOGIC")
print("="*80)

# Check if there are any trades with EXIT events but high No BE MFE
cur.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe
    FROM automated_signals
    WHERE event_type LIKE 'EXIT_%'
    AND no_be_mfe > 1.0
    ORDER BY timestamp DESC
    LIMIT 5
""")

suspicious = cur.fetchall()
if suspicious:
    print(f"\n⚠️  FOUND {len(suspicious)} SUSPICIOUS COMPLETED TRADES:")
    print("(Marked as EXIT but No BE MFE > 1.0R suggests they shouldn't have stopped)")
    for trade_id, event_type, be_mfe, no_be_mfe in suspicious:
        print(f"\n  Trade: {trade_id}")
        print(f"    Event: {event_type}")
        print(f"    BE MFE: {be_mfe}R")
        print(f"    No BE MFE: {no_be_mfe}R")
        print(f"    ⚠️  This trade shows EXIT but No BE MFE suggests it's still running!")

cur.close()
conn.close()

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
