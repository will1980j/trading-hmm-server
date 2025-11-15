import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("DIAGNOSING COMPLETION STATUS AND MFE VALUES")
print("=" * 80)

# Get all unique trade_ids
cur.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    ORDER BY trade_id DESC 
    LIMIT 20
""")
trade_ids = [row[0] for row in cur.fetchall()]

print(f"\nAnalyzing {len(trade_ids)} most recent trades...\n")

for trade_id in trade_ids:
    print(f"\n{'='*80}")
    print(f"TRADE: {trade_id}")
    print(f"{'='*80}")
    
    # Get all events for this trade
    cur.execute("""
        SELECT event_type, be_mfe, no_be_mfe, mfe, timestamp, 
               entry_price, stop_loss, direction
        FROM automated_signals 
        WHERE trade_id = %s 
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    events = cur.fetchall()
    
    print(f"\nTotal Events: {len(events)}")
    print(f"\nEvent Timeline:")
    print("-" * 80)
    
    has_exit = False
    has_be_triggered = False
    latest_mfe_update = None
    
    for event in events:
        event_type, be_mfe, no_be_mfe, mfe, timestamp, entry, stop, direction = event
        
        print(f"{timestamp} | {event_type:20s} | BE_MFE: {be_mfe} | NO_BE_MFE: {no_be_mfe} | MFE: {mfe}")
        
        if event_type == 'EXIT_STOP_LOSS':
            has_exit = True
        elif event_type == 'EXIT_BREAK_EVEN':
            has_be_triggered = True
        elif event_type == 'MFE_UPDATE':
            latest_mfe_update = (be_mfe, no_be_mfe, mfe)
    
    print("-" * 80)
    
    # Determine actual status
    if has_exit or has_be_triggered:
        actual_status = "COMPLETED"
        completion_reason = "EXIT_STOP_LOSS" if has_exit else "EXIT_BREAK_EVEN"
    else:
        actual_status = "ACTIVE"
        completion_reason = "N/A"
    
    print(f"\nACTUAL STATUS: {actual_status}")
    print(f"COMPLETION REASON: {completion_reason}")
    
    if latest_mfe_update:
        be_mfe, no_be_mfe, mfe = latest_mfe_update
        print(f"\nLATEST MFE VALUES:")
        print(f"  BE_MFE: {be_mfe}")
        print(f"  NO_BE_MFE: {no_be_mfe}")
        print(f"  MFE (legacy): {mfe}")
    else:
        print(f"\nNO MFE_UPDATE EVENTS FOUND!")
    
    # Check what the API query would return
    cur.execute("""
        SELECT 
            t.trade_id,
            t.direction,
            t.entry_price,
            t.stop_loss,
            t.session,
            t.bias,
            t.signal_date,
            t.signal_time,
            COALESCE(
                (SELECT event_type FROM automated_signals 
                 WHERE trade_id = t.trade_id 
                 AND event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN')
                 ORDER BY timestamp DESC LIMIT 1),
                'ACTIVE'
            ) as status,
            (SELECT be_mfe FROM automated_signals 
             WHERE trade_id = t.trade_id 
             AND event_type = 'MFE_UPDATE'
             ORDER BY timestamp DESC LIMIT 1) as be_mfe,
            (SELECT no_be_mfe FROM automated_signals 
             WHERE trade_id = t.trade_id 
             AND event_type = 'MFE_UPDATE'
             ORDER BY timestamp DESC LIMIT 1) as no_be_mfe
        FROM (
            SELECT DISTINCT ON (trade_id) *
            FROM automated_signals
            WHERE trade_id = %s
            ORDER BY trade_id, timestamp DESC
        ) t
    """, (trade_id,))
    
    api_result = cur.fetchone()
    if api_result:
        print(f"\nAPI QUERY RESULT:")
        print(f"  Status: {api_result[8]}")
        print(f"  BE_MFE: {api_result[9]}")
        print(f"  NO_BE_MFE: {api_result[10]}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)

cur.close()
conn.close()
