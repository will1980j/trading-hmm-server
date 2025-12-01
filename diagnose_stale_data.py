#!/usr/bin/env python3
"""Diagnose why dashboard shows stale/old data"""
import os
import psycopg2
from datetime import datetime, timedelta
import pytz

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

eastern = pytz.timezone('US/Eastern')
now_eastern = datetime.now(eastern)
print(f"Current time (Eastern): {now_eastern.strftime('%Y-%m-%d %H:%M:%S')}")

# Check what dates are in the database
print("\n=== DATES IN DATABASE ===")
cur.execute("""
    SELECT DATE(timestamp) as date, COUNT(*) as count
    FROM automated_signals
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} events")

# Check today's signals specifically
print("\n=== TODAY'S SIGNALS (Dec 1, 2025) ===")
cur.execute("""
    SELECT trade_id, event_type, timestamp, signal_date, signal_time, session
    FROM automated_signals
    WHERE DATE(timestamp) = '2025-12-01'
    ORDER BY timestamp DESC
    LIMIT 20
""")
rows = cur.fetchall()
print(f"Found {len(rows)} events today")
for row in rows[:10]:
    print(f"  {row[0][:30]}... | {row[1]:15} | ts={row[2]} | date={row[3]} | time={row[4]} | session={row[5]}")

# Check ENTRY events specifically
print("\n=== ENTRY EVENTS (most recent) ===")
cur.execute("""
    SELECT trade_id, timestamp, signal_date, signal_time, session, direction
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0][:30]}... | ts={row[1]} | date={row[2]} | time={row[3]} | session={row[4]} | dir={row[5]}")

# Check if there are EXIT events for these trades
print("\n=== ACTIVE vs COMPLETED COUNTS ===")
cur.execute("""
    SELECT 
        (SELECT COUNT(DISTINCT trade_id) FROM automated_signals WHERE event_type = 'ENTRY') as total_entries,
        (SELECT COUNT(DISTINCT trade_id) FROM automated_signals WHERE event_type LIKE 'EXIT_%') as total_exits
""")
row = cur.fetchone()
print(f"  Total ENTRY events: {row[0]}")
print(f"  Total EXIT events: {row[1]}")
print(f"  Active trades (no exit): {row[0] - row[1]}")

# Check the trade_id format - are they from today?
print("\n=== TRADE ID ANALYSIS ===")
cur.execute("""
    SELECT trade_id FROM automated_signals 
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 10
""")
for row in cur.fetchall():
    trade_id = row[0]
    # Trade ID format: YYYYMMDD_HHMMSS000_DIRECTION
    if '_' in trade_id:
        date_part = trade_id.split('_')[0]
        print(f"  {trade_id} -> Date from ID: {date_part}")

conn.close()
