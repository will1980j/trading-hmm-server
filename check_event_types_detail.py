#!/usr/bin/env python3
"""Check event types in detail"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check all event types
print("=== ALL EVENT TYPES ===")
cur.execute("SELECT DISTINCT event_type FROM automated_signals")
for row in cur.fetchall():
    print(f"  '{row[0]}'")

# Check a specific trade to see all its events
print("\n=== EVENTS FOR TRADE 20251128_094800000_BULLISH ===")
cur.execute("""
    SELECT id, event_type, mfe, be_mfe, no_be_mfe, entry_price, timestamp
    FROM automated_signals 
    WHERE trade_id = '20251128_094800000_BULLISH'
    ORDER BY timestamp
""")
for row in cur.fetchall():
    print(f"  ID={row[0]}, type='{row[1]}', mfe={row[2]}, be_mfe={row[3]}, entry={row[5]}, ts={row[6]}")

# Check if there are any ENTRY events at all
print("\n=== COUNT OF ENTRY EVENTS ===")
cur.execute("SELECT COUNT(*) FROM automated_signals WHERE event_type = 'ENTRY'")
print(f"  ENTRY events: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM automated_signals WHERE event_type LIKE '%ENTRY%'")
print(f"  Events containing 'ENTRY': {cur.fetchone()[0]}")

# Check what the first event for each trade looks like
print("\n=== FIRST EVENT FOR RECENT TRADES ===")
cur.execute("""
    SELECT DISTINCT ON (trade_id) trade_id, event_type, timestamp
    FROM automated_signals
    ORDER BY trade_id, timestamp
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]}: first event = '{row[1]}' at {row[2]}")

cur.close()
conn.close()
