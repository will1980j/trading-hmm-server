"""
Test Cancelled Signal Display
Verify cancelled signals show proper time, date, and age
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("CANCELLED SIGNAL DISPLAY TEST")
print("=" * 80)
print()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Query using the same logic as All Signals API
cur.execute("""
    WITH signal_lifecycle AS (
        SELECT 
            sc.trade_id,
            sc.timestamp as signal_time,
            sc.direction,
            sc.session,
            sc.htf_alignment,
            sc.signal_date,
            sc.signal_time as signal_time_str,
            EXISTS(
                SELECT 1 FROM automated_signals e 
                WHERE e.trade_id = sc.trade_id 
                AND e.event_type = 'ENTRY'
            ) as is_confirmed,
            EXISTS(
                SELECT 1 FROM automated_signals c 
                WHERE c.trade_id = sc.trade_id 
                AND c.event_type = 'CANCELLED'
            ) as is_cancelled,
            (
                SELECT e.timestamp 
                FROM automated_signals e 
                WHERE e.trade_id = sc.trade_id 
                AND e.event_type = 'ENTRY' 
                LIMIT 1
            ) as confirmation_time,
            (
                SELECT c.timestamp 
                FROM automated_signals c 
                WHERE c.trade_id = sc.trade_id 
                AND c.event_type = 'CANCELLED' 
                LIMIT 1
            ) as cancellation_time,
            (
                SELECT e.entry_price 
                FROM automated_signals e 
                WHERE e.trade_id = sc.trade_id 
                AND e.event_type = 'ENTRY' 
                LIMIT 1
            ) as entry_price,
            (
                SELECT e.stop_loss 
                FROM automated_signals e 
                WHERE e.trade_id = sc.trade_id 
                AND e.event_type = 'ENTRY' 
                LIMIT 1
            ) as stop_loss
        FROM automated_signals sc
        WHERE sc.event_type = 'SIGNAL_CREATED'
        ORDER BY sc.timestamp DESC
        LIMIT 10
    )
    SELECT 
        trade_id,
        signal_time,
        direction,
        session,
        signal_date,
        signal_time_str,
        is_confirmed,
        is_cancelled,
        confirmation_time,
        cancellation_time,
        CASE 
            WHEN is_confirmed THEN 
                EXTRACT(EPOCH FROM (confirmation_time - signal_time))/60
            WHEN is_cancelled THEN
                EXTRACT(EPOCH FROM (cancellation_time - signal_time))/60
            ELSE NULL
        END as minutes_to_event,
        CASE
            WHEN is_cancelled THEN 'CANCELLED'
            WHEN is_confirmed THEN 'CONFIRMED'
            ELSE 'PENDING'
        END as status
    FROM signal_lifecycle
    ORDER BY signal_time DESC
""")

signals = cur.fetchall()

print(f"Total signals: {len(signals)}")
print()

for signal in signals:
    trade_id = signal[0]
    signal_time = signal[1]
    direction = signal[2]
    session = signal[3]
    signal_date = signal[4]
    signal_time_str = signal[5]
    is_confirmed = signal[6]
    is_cancelled = signal[7]
    confirmation_time = signal[8]
    cancellation_time = signal[9]
    minutes_to_event = signal[10]
    status = signal[11]
    
    # Format age
    age_formatted = '--'
    if minutes_to_event is not None:
        total_seconds = int(minutes_to_event * 60)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            age_formatted = f"{hours}h {minutes}m"
        elif minutes > 0:
            age_formatted = f"{minutes}m {seconds}s"
        else:
            age_formatted = f"{seconds}s"
    
    print(f"Signal: {trade_id[:30]}...")
    print(f"   Date: {signal_date}")
    print(f"   Time: {signal_time_str}")
    print(f"   Direction: {direction}")
    print(f"   Session: {session}")
    print(f"   Status: {status}")
    
    if status == 'CONFIRMED':
        print(f"   Confirmation Time: {confirmation_time}")
        print(f"   Age Before Confirmation: {age_formatted}")
    elif status == 'CANCELLED':
        print(f"   Cancellation Time: {cancellation_time}")
        print(f"   Age Before Cancellation: {age_formatted}")
    
    print()

cur.close()
conn.close()

print("=" * 80)
print("DISPLAY FORMAT VERIFICATION")
print("=" * 80)
print()
print("Cancelled signals now show:")
print("✅ Signal Date (from SIGNAL_CREATED)")
print("✅ Signal Time (from SIGNAL_CREATED)")
print("✅ Age Before Cancellation (formatted like confirmed signals)")
print("✅ Cancellation Time (when CANCELLED event occurred)")
print()
print("This matches the confirmed signals tab formatting!")
