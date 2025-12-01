#!/usr/bin/env python3
"""Check webhook logs for today"""
import os
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check if webhook_logs table exists
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'webhook_logs'
    )
""")
has_webhook_logs = cur.fetchone()[0]
print(f"webhook_logs table exists: {has_webhook_logs}")

if has_webhook_logs:
    # Check recent webhook logs
    print("\n=== RECENT WEBHOOK LOGS ===")
    cur.execute("""
        SELECT id, endpoint, status, timestamp, error_message
        FROM webhook_logs
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    for row in cur.fetchall():
        print(f"  ID={row[0]}, endpoint={row[1]}, status={row[2]}, ts={row[3]}")
        if row[4]:
            print(f"    error: {row[4][:100]}")

# Check most recent automated_signals entry
print("\n=== MOST RECENT AUTOMATED_SIGNALS ENTRIES ===")
cur.execute("""
    SELECT id, trade_id, event_type, timestamp
    FROM automated_signals
    ORDER BY timestamp DESC
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  ID={row[0]}, trade={row[1]}, type={row[2]}, ts={row[3]}")

# Check if there's any data from today (Dec 1)
print("\n=== DATA FROM TODAY (Dec 1, 2025) ===")
cur.execute("""
    SELECT COUNT(*) 
    FROM automated_signals 
    WHERE timestamp >= '2025-12-01 00:00:00'
""")
print(f"  Events today: {cur.fetchone()[0]}")

# Check data from last 3 days
print("\n=== DATA BY DAY (last 7 days) ===")
cur.execute("""
    SELECT DATE(timestamp) as day, COUNT(*) 
    FROM automated_signals 
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY DATE(timestamp)
    ORDER BY day DESC
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} events")

cur.close()
conn.close()
