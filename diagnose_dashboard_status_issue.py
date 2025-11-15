import os
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL')

def diagnose_status_and_mfe():
    """Diagnose why all trades show as completed and missing MFE values"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("AUTOMATED SIGNALS STATUS & MFE DIAGNOSTIC")
    print("=" * 80)
    
    # Get today's date
    today = datetime.now().date()
    
    # Check what the dashboard API is returning
    print("\n1. CHECKING WHAT DASHBOARD API RETURNS:")
    print("-" * 80)
    
    query = """
        WITH latest_events AS (
            SELECT DISTINCT ON (trade_id)
                trade_id,
                event_type,
                direction,
                entry_price,
                stop_loss,
                be_mfe,
                no_be_mfe,
                session,
                signal_time,
                timestamp,
                signal_date
            FROM automated_signals
            WHERE signal_date = %s
            ORDER BY trade_id, timestamp DESC
        )
        SELECT 
            trade_id,
            event_type,
            direction,
            entry_price,
            stop_loss,
            be_mfe,
            no_be_mfe,
            session,
            signal_time
        FROM latest_events
        ORDER BY signal_time DESC
        LIMIT 10;
    """
    
    cur.execute(query, (today,))
    results = cur.fetchall()
    
    print(f"\nFound {len(results)} trades for today ({today})")
    print("\nTrade Details:")
    for row in results:
        trade_id, event_type, direction, entry, sl, be_mfe, no_be_mfe, session, sig_time = row
        print(f"\n  Trade ID: {trade_id}")
        print(f"  Latest Event Type: {event_type}")
        print(f"  Direction: {direction}")
        print(f"  Entry: {entry}")
        print(f"  Stop Loss: {sl}")
        print(f"  BE MFE: {be_mfe}")
        print(f"  No BE MFE: {no_be_mfe}")
        print(f"  Session: {session}")
        print(f"  Signal Time: {sig_time}")
        
        # Determine what status SHOULD be shown
        if event_type in ['EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN']:
            expected_status = "COMPLETED"
        elif event_type in ['ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED']:
            expected_status = "ACTIVE"
        else:
            expected_status = "UNKNOWN"
        
        print(f"  Expected Status: {expected_status}")
    
    # Check all events for a specific trade to see the full lifecycle
    print("\n\n2. CHECKING FULL EVENT HISTORY FOR FIRST TRADE:")
    print("-" * 80)
    
    if results:
        first_trade_id = results[0][0]
        
        query = """
            SELECT 
                event_type,
                be_mfe,
                no_be_mfe,
                timestamp,
                signal_time
            FROM automated_signals
            WHERE trade_id = %s
            ORDER BY timestamp ASC;
        """
        
        cur.execute(query, (first_trade_id,))
        events = cur.fetchall()
        
        print(f"\nTrade ID: {first_trade_id}")
        print(f"Total Events: {len(events)}")
        print("\nEvent Timeline:")
        for event in events:
            event_type, be_mfe, no_be_mfe, ts, sig_time = event
            print(f"  {ts} | {event_type:20s} | BE MFE: {be_mfe or 'NULL':>8s} | No BE MFE: {no_be_mfe or 'NULL':>8s}")
    
    # Check for trades with missing MFE
    print("\n\n3. CHECKING TRADES WITH MISSING MFE VALUES:")
    print("-" * 80)
    
    query = """
        WITH latest_events AS (
            SELECT DISTINCT ON (trade_id)
                trade_id,
                event_type,
                be_mfe,
                no_be_mfe,
                signal_time
            FROM automated_signals
            WHERE signal_date = %s
            ORDER BY trade_id, timestamp DESC
        )
        SELECT 
            trade_id,
            event_type,
            be_mfe,
            no_be_mfe
        FROM latest_events
        WHERE (be_mfe IS NULL OR be_mfe = 0) 
           OR (no_be_mfe IS NULL OR no_be_mfe = 0)
        ORDER BY signal_time DESC;
    """
    
    cur.execute(query, (today,))
    missing_mfe = cur.fetchall()
    
    print(f"\nFound {len(missing_mfe)} trades with missing/zero MFE values:")
    for row in missing_mfe:
        trade_id, event_type, be_mfe, no_be_mfe = row
        print(f"  {trade_id} | Event: {event_type:20s} | BE: {be_mfe or 'NULL'} | No BE: {no_be_mfe or 'NULL'}")
    
    # Check event type distribution
    print("\n\n4. EVENT TYPE DISTRIBUTION FOR TODAY:")
    print("-" * 80)
    
    query = """
        SELECT 
            event_type,
            COUNT(*) as count
        FROM automated_signals
        WHERE signal_date = %s
        GROUP BY event_type
        ORDER BY count DESC;
    """
    
    cur.execute(query, (today,))
    event_dist = cur.fetchall()
    
    print("\nEvent Type Counts:")
    for event_type, count in event_dist:
        print(f"  {event_type:20s}: {count}")
    
    # Check what the latest event is for each trade
    print("\n\n5. LATEST EVENT TYPE FOR EACH TRADE:")
    print("-" * 80)
    
    query = """
        WITH latest_events AS (
            SELECT DISTINCT ON (trade_id)
                trade_id,
                event_type,
                timestamp
            FROM automated_signals
            WHERE signal_date = %s
            ORDER BY trade_id, timestamp DESC
        )
        SELECT 
            event_type,
            COUNT(*) as count
        FROM latest_events
        GROUP BY event_type
        ORDER BY count DESC;
    """
    
    cur.execute(query, (today,))
    latest_events = cur.fetchall()
    
    print("\nLatest Event Type Distribution:")
    for event_type, count in latest_events:
        print(f"  {event_type:20s}: {count} trades")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_status_and_mfe()
