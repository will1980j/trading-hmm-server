"""
Check what data is actually in SIGNAL_CREATED events
"""

import psycopg2
import os
from dotenv import load_dotenv
import json

load_dotenv()

database_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(database_url)
cur = conn.cursor()

print("=" * 80)
print("SIGNAL_CREATED DATA ANALYSIS")
print("=" * 80)
print()

# Check if SIGNAL_CREATED events exist
cur.execute("""
    SELECT COUNT(*) 
    FROM automated_signals 
    WHERE event_type = 'SIGNAL_CREATED'
""")

signal_created_count = cur.fetchone()[0]
print(f"Total SIGNAL_CREATED events: {signal_created_count}")

if signal_created_count == 0:
    print("\n⚠️ NO SIGNAL_CREATED EVENTS FOUND!")
    print("This means the indicator is not sending SIGNAL_CREATED webhooks.")
    print("We need to add SIGNAL_CREATED webhook to the indicator.")
else:
    # Get sample SIGNAL_CREATED event
    cur.execute("""
        SELECT 
            trade_id,
            timestamp,
            direction,
            session,
            signal_date,
            signal_time,
            htf_alignment,
            raw_payload
        FROM automated_signals
        WHERE event_type = 'SIGNAL_CREATED'
        ORDER BY timestamp DESC
        LIMIT 1
    """)
    
    row = cur.fetchone()
    
    print()
    print("=" * 80)
    print("SAMPLE SIGNAL_CREATED EVENT")
    print("=" * 80)
    print(f"Trade ID: {row[0]}")
    print(f"Timestamp: {row[1]}")
    print(f"Direction: {row[2]}")
    print(f"Session: {row[3]}")
    print(f"Signal Date: {row[4]}")
    print(f"Signal Time: {row[5]}")
    print(f"HTF Alignment: {row[6]}")
    print()
    print("Raw Payload:")
    if row[7]:
        payload = row[7] if isinstance(row[7], dict) else json.loads(row[7])
        print(json.dumps(payload, indent=2))
    else:
        print("  (None)")

# Check ENTRY events for comparison
print()
print("=" * 80)
print("ENTRY EVENT DATA (for comparison)")
print("=" * 80)

cur.execute("""
    SELECT 
        trade_id,
        htf_alignment,
        session,
        signal_date,
        signal_time,
        confirmation_time,
        bars_to_confirmation
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 1
""")

row = cur.fetchone()
print(f"Trade ID: {row[0]}")
print(f"HTF Alignment: {row[1]}")
print(f"Session: {row[2]}")
print(f"Signal Date: {row[3]}")
print(f"Signal Time: {row[4]}")
print(f"Confirmation Time: {row[5]}")
print(f"Bars to Confirmation: {row[6]}")

cur.close()
conn.close()

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
