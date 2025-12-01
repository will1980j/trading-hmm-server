#!/usr/bin/env python3
"""Check raw database data to understand what's stored"""
import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check what columns exist
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'automated_signals'
    ORDER BY ordinal_position
""")
print("=== COLUMNS IN automated_signals ===")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check a few recent ENTRY events
print("\n=== RECENT ENTRY EVENTS (raw data) ===")
cur.execute("""
    SELECT trade_id, event_type, direction, entry_price, mfe, be_mfe, no_be_mfe, 
           signal_date, signal_time, timestamp, session
    FROM automated_signals 
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"Trade: {row[0]}")
    print(f"  event_type: {row[1]}")
    print(f"  direction: {row[2]}")
    print(f"  entry_price: {row[3]}")
    print(f"  mfe: {row[4]}")
    print(f"  be_mfe: {row[5]}")
    print(f"  no_be_mfe: {row[6]}")
    print(f"  signal_date: {row[7]}")
    print(f"  signal_time: {row[8]}")
    print(f"  timestamp: {row[9]}")
    print(f"  session: {row[10]}")
    print()

# Check if there are MFE_UPDATE events
print("\n=== MFE_UPDATE EVENTS COUNT ===")
cur.execute("SELECT COUNT(*) FROM automated_signals WHERE event_type = 'MFE_UPDATE'")
print(f"MFE_UPDATE events: {cur.fetchone()[0]}")

# Check what event types exist
print("\n=== EVENT TYPES IN DATABASE ===")
cur.execute("SELECT event_type, COUNT(*) FROM automated_signals GROUP BY event_type ORDER BY COUNT(*) DESC")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
