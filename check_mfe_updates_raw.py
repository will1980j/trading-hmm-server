#!/usr/bin/env python3
"""Check MFE_UPDATE events to see where MFE data is stored"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check MFE_UPDATE events for a specific trade
print("=== MFE_UPDATE EVENTS FOR RECENT TRADES ===")
cur.execute("""
    SELECT trade_id, event_type, mfe, be_mfe, no_be_mfe, timestamp
    FROM automated_signals 
    WHERE event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"Trade: {row[0]}")
    print(f"  mfe: {row[2]}, be_mfe: {row[3]}, no_be_mfe: {row[4]}")
    print(f"  timestamp: {row[5]}")
    print()

# Check today's trades specifically
print("\n=== TODAY'S TRADES (Dec 1) ===")
cur.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE trade_id LIKE '20251201%'
    ORDER BY trade_id
""")
today_trades = [row[0] for row in cur.fetchall()]
print(f"Found {len(today_trades)} trades today: {today_trades}")

# For each today's trade, show all events
for trade_id in today_trades[:3]:
    print(f"\n=== ALL EVENTS FOR {trade_id} ===")
    cur.execute("""
        SELECT event_type, mfe, be_mfe, no_be_mfe, entry_price, timestamp
        FROM automated_signals 
        WHERE trade_id = %s
        ORDER BY timestamp
    """, (trade_id,))
    for row in cur.fetchall():
        print(f"  {row[0]}: mfe={row[1]}, be_mfe={row[2]}, no_be_mfe={row[3]}, entry={row[4]}, ts={row[5]}")

cur.close()
conn.close()
