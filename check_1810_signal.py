"""
Check the 18:10 signal to see what webhooks were actually sent
"""
import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Set it with: $env:DATABASE_URL='your_railway_url'")
    exit(1)

def check_1810_signal():
    """Check all events for the 18:10 signal"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("CHECKING 18:10 SIGNAL")
    print("="*80)
    
    # Get all signals from around 18:10 (6:10 PM)
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
        WHERE signal_time LIKE '%18:1%' OR signal_time LIKE '%6:1%'
        ORDER BY trade_id, timestamp
    """)
    
    results = cur.fetchall()
    
    if not results:
        print("\n❌ No signals found around 18:10")
        print("Checking last 30 minutes instead...")
        
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
            WHERE timestamp > NOW() - INTERVAL '30 minutes'
            ORDER BY trade_id, timestamp
        """)
        
        results = cur.fetchall()
    
    if not results:
        print("\n❌ No signals in last 30 minutes")
        return
    
    # Group by trade_id
    trades = {}
    for row in results:
        trade_id = row[0]
        if trade_id not in trades:
            trades[trade_id] = []
        trades[trade_id].append(row)
    
    print(f"\nFound {len(trades)} trade(s):")
    print("="*80)
    
    for trade_id, events in trades.items():
        print(f"\n📊 Trade ID: {trade_id}")
        print("-"*80)
        
        first_event_time = events[0][10]
        last_event_time = events[-1][10]
        time_span = (last_event_time - first_event_time).total_seconds()
        
        print(f"First event: {first_event_time}")
        print(f"Last event: {last_event_time}")
        print(f"Time span: {time_span:.3f} seconds")
        
        if time_span < 1.0:
            print("⚠️  ALL EVENTS SENT IN LESS THAN 1 SECOND - HISTORICAL REPLAY!")
        
        print(f"\nEvent sequence ({len(events)} events):")
        for i, event in enumerate(events, 1):
            (tid, event_type, direction, entry, stop, risk, be_mfe, no_be_mfe, 
             sig_date, sig_time, timestamp) = event
            
            ms_from_first = (timestamp - first_event_time).total_seconds() * 1000
            
            print(f"\n{i}. {event_type} (+{ms_from_first:.1f}ms)")
            print(f"   Time: {timestamp}")
            if direction:
                print(f"   Direction: {direction}")
            if entry:
                print(f"   Entry: {entry}, Stop: {stop}, Risk: {risk}")
            if be_mfe is not None or no_be_mfe is not None:
                print(f"   BE MFE: {be_mfe}, No BE MFE: {no_be_mfe}")
        
        # Check if barstate.isrealtime was working
        event_types = [e[1] for e in events]
        if 'EXIT_STOP_LOSS' in event_types or 'EXIT_BREAK_EVEN' in event_types:
            exit_index = next(i for i, e in enumerate(events) if e[1] in ['EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN'])
            if exit_index < len(events) - 1:
                print("\n❌ CRITICAL: EXIT event is NOT the last event!")
                print("   This means events are out of order or being replayed")
            else:
                print("\n⚠️  EXIT event is last, but came too quickly")
                print("   Indicator may still be processing historical bars")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_1810_signal()
