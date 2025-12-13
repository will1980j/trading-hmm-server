"""
Detailed check of SIGNAL_CREATED events in database
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
print("DETAILED SIGNAL_CREATED ANALYSIS")
print("=" * 80)
print()

# Check all event types
print("1. ALL EVENT TYPES IN DATABASE:")
cur.execute("""
    SELECT event_type, COUNT(*) as count
    FROM automated_signals
    GROUP BY event_type
    ORDER BY count DESC
""")

for row in cur.fetchall():
    print(f"   {row[0]}: {row[1]}")

print()
print("=" * 80)

# Check specifically for SIGNAL_CREATED
print("2. SIGNAL_CREATED EVENTS:")
cur.execute("""
    SELECT COUNT(*) 
    FROM automated_signals 
    WHERE event_type = 'SIGNAL_CREATED'
""")

signal_created_count = cur.fetchone()[0]
print(f"   Total: {signal_created_count}")

if signal_created_count > 0:
    print()
    print("   Sample SIGNAL_CREATED events:")
    cur.execute("""
        SELECT 
            trade_id,
            timestamp,
            direction,
            session,
            htf_alignment,
            raw_payload
        FROM automated_signals
        WHERE event_type = 'SIGNAL_CREATED'
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        print(f"\n   Trade ID: {row[0]}")
        print(f"   Timestamp: {row[1]}")
        print(f"   Direction: {row[2]}")
        print(f"   Session: {row[3]}")
        print(f"   HTF Alignment: {row[4]}")
        if row[5]:
            print(f"   Raw Payload Keys: {list(row[5].keys()) if isinstance(row[5], dict) else 'N/A'}")

print()
print("=" * 80)

# Check for recent signals (last 24 hours)
print("3. RECENT SIGNALS (LAST 24 HOURS):")
cur.execute("""
    SELECT 
        event_type,
        COUNT(*) as count
    FROM automated_signals
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY event_type
    ORDER BY count DESC
""")

for row in cur.fetchall():
    print(f"   {row[0]}: {row[1]}")

print()
print("=" * 80)

# Check if ENTRY events have corresponding SIGNAL_CREATED
print("4. ENTRY EVENTS WITHOUT SIGNAL_CREATED:")
cur.execute("""
    SELECT COUNT(DISTINCT e.trade_id)
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND NOT EXISTS (
        SELECT 1 FROM automated_signals sc
        WHERE sc.trade_id = e.trade_id
        AND sc.event_type = 'SIGNAL_CREATED'
    )
""")

entry_without_signal_created = cur.fetchone()[0]
print(f"   ENTRY events without SIGNAL_CREATED: {entry_without_signal_created}")

print()
print("=" * 80)

# Check webhook logs for SIGNAL_CREATED
print("5. CHECKING WEBHOOK RECEPTION:")
cur.execute("""
    SELECT 
        raw_payload->>'event_type' as event_type,
        COUNT(*) as count
    FROM automated_signals
    WHERE raw_payload IS NOT NULL
    AND timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY raw_payload->>'event_type'
    ORDER BY count DESC
""")

print("   Event types in raw_payload (last 24h):")
for row in cur.fetchall():
    if row[0]:
        print(f"   {row[0]}: {row[1]}")

cur.close()
conn.close()

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
