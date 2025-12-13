"""
Check if SIGNAL_CREATED events existed in the past but were deleted
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(database_url)
cur = conn.cursor()

print("=" * 80)
print("SIGNAL_CREATED HISTORY INVESTIGATION")
print("=" * 80)
print()

# Check oldest and newest events
print("1. EVENT TIMELINE:")
cur.execute("""
    SELECT 
        event_type,
        MIN(timestamp) as oldest,
        MAX(timestamp) as newest,
        COUNT(*) as count
    FROM automated_signals
    GROUP BY event_type
    ORDER BY oldest ASC
""")

print("   Event Type          | Oldest              | Newest              | Count")
print("   " + "-" * 75)
for row in cur.fetchall():
    print(f"   {row[0]:20} | {row[1]} | {row[2]} | {row[3]}")

print()
print("=" * 80)

# Check if there are any references to SIGNAL_CREATED in raw_payload
print("2. CHECKING RAW PAYLOADS FOR SIGNAL_CREATED REFERENCES:")
cur.execute("""
    SELECT COUNT(*)
    FROM automated_signals
    WHERE raw_payload::text LIKE '%SIGNAL_CREATED%'
""")

signal_created_refs = cur.fetchone()[0]
print(f"   Events with 'SIGNAL_CREATED' in raw_payload: {signal_created_refs}")

if signal_created_refs > 0:
    print("\n   Sample events:")
    cur.execute("""
        SELECT 
            trade_id,
            event_type,
            timestamp,
            raw_payload::text
        FROM automated_signals
        WHERE raw_payload::text LIKE '%SIGNAL_CREATED%'
        LIMIT 3
    """)
    
    for row in cur.fetchall():
        print(f"\n   Trade ID: {row[0]}")
        print(f"   Event Type: {row[1]}")
        print(f"   Timestamp: {row[2]}")
        print(f"   Payload snippet: {row[3][:200]}...")

print()
print("=" * 80)

# Check sync_audit_log for SIGNAL_CREATED activity
print("3. CHECKING SYNC AUDIT LOG:")
try:
    cur.execute("""
        SELECT COUNT(*)
        FROM sync_audit_log
        WHERE action_type LIKE '%signal_created%'
        OR fields_filled::text LIKE '%signal_created%'
    """)
    
    audit_refs = cur.fetchone()[0]
    print(f"   Audit log entries mentioning SIGNAL_CREATED: {audit_refs}")
except Exception as e:
    print(f"   Sync audit log not available yet: {e}")

print()
print("=" * 80)

# Check if ENTRY events have signal_date/signal_time (which would come from SIGNAL_CREATED)
print("4. CHECKING ENTRY EVENTS FOR SIGNAL_CREATED DATA:")
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(signal_date) as has_signal_date,
        COUNT(signal_time) as has_signal_time,
        COUNT(htf_alignment) as has_htf_alignment,
        COUNT(confirmation_time) as has_confirmation_time
    FROM automated_signals
    WHERE event_type = 'ENTRY'
""")

row = cur.fetchone()
print(f"   Total ENTRY events: {row[0]}")
print(f"   With signal_date: {row[1]}")
print(f"   With signal_time: {row[2]}")
print(f"   With htf_alignment: {row[3]}")
print(f"   With confirmation_time: {row[4]}")

print()
print("=" * 80)

# Check the All Signals API to see what it returns
print("5. TESTING ALL SIGNALS API QUERY:")
cur.execute("""
    SELECT COUNT(*)
    FROM automated_signals
    WHERE event_type = 'SIGNAL_CREATED'
""")

signal_created_count = cur.fetchone()[0]
print(f"   SIGNAL_CREATED events (what All Signals API would show): {signal_created_count}")

# Alternative: Show what ENTRY events exist (which All Signals tab might have been showing)
cur.execute("""
    SELECT 
        trade_id,
        timestamp,
        direction,
        session,
        signal_date,
        signal_time
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 5
""")

print("\n   Recent ENTRY events (might have been shown as 'signals'):")
for row in cur.fetchall():
    print(f"   - {row[0]} | {row[1]} | {row[2]} | {row[3]}")

cur.close()
conn.close()

print()
print("=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
print()
print("CONCLUSION:")
print("If you saw signals in All Signals tab, either:")
print("1. SIGNAL_CREATED events existed but were deleted")
print("2. The tab was showing ENTRY events instead")
print("3. The tab was showing data from a different source")
