#!/usr/bin/env python3
"""Check all recent trades in database"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get all unique trade_ids ordered by most recent
print("=== ALL UNIQUE TRADE IDS (most recent first) ===")
cur.execute("""
    SELECT DISTINCT trade_id, MAX(timestamp) as latest
    FROM automated_signals 
    GROUP BY trade_id
    ORDER BY latest DESC
    LIMIT 20
""")
for row in cur.fetchall():
    print(f"  {row[0]} - last event: {row[1]}")

# Check what the dashboard query is actually returning
print("\n=== SIMULATING DASHBOARD QUERY ===")
cur.execute("""
    WITH latest_events AS (
        SELECT trade_id, 
               MAX(CASE WHEN event_type = 'ENTRY' THEN timestamp END) as entry_time,
               MAX(CASE WHEN event_type IN ('EXIT_STOP_LOSS', 'EXIT_BE') THEN timestamp END) as exit_time,
               MAX(timestamp) as last_update
        FROM automated_signals
        GROUP BY trade_id
    )
    SELECT le.trade_id,
           CASE WHEN le.exit_time IS NOT NULL THEN 'COMPLETED' ELSE 'ACTIVE' END as status,
           le.entry_time,
           le.exit_time,
           le.last_update
    FROM latest_events le
    ORDER BY le.last_update DESC
    LIMIT 15
""")
print(f"{'Trade ID':<40} {'Status':<12} {'Entry Time':<25} {'Exit Time':<25}")
print("-" * 110)
for row in cur.fetchall():
    print(f"{row[0]:<40} {row[1]:<12} {str(row[2]):<25} {str(row[3]):<25}")

# Count active vs completed
print("\n=== TRADE STATUS COUNTS ===")
cur.execute("""
    WITH trade_status AS (
        SELECT trade_id,
               CASE WHEN EXISTS (
                   SELECT 1 FROM automated_signals a2 
                   WHERE a2.trade_id = automated_signals.trade_id 
                   AND a2.event_type IN ('EXIT_STOP_LOSS', 'EXIT_BE')
               ) THEN 'COMPLETED' ELSE 'ACTIVE' END as status
        FROM automated_signals
        GROUP BY trade_id
    )
    SELECT status, COUNT(*) FROM trade_status GROUP BY status
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
