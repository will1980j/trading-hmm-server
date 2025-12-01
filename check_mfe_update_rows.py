#!/usr/bin/env python3
"""Check what MFE_UPDATE rows look like in the database"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check MFE_UPDATE rows
cur.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, mfe, current_price, timestamp
    FROM automated_signals 
    WHERE event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 10
""")

print("=== MFE_UPDATE ROWS ===")
for row in cur.fetchall():
    print(f"trade_id={row[0][:25]}... | be_mfe={row[2]} | no_be_mfe={row[3]} | mfe={row[4]} | price={row[5]} | ts={row[6]}")

# Check ENTRY rows with MFE values
cur.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, mfe, current_price, timestamp
    FROM automated_signals 
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 10
""")

print("\n=== ENTRY ROWS (with MFE) ===")
for row in cur.fetchall():
    print(f"trade_id={row[0][:25]}... | be_mfe={row[2]} | no_be_mfe={row[3]} | mfe={row[4]} | price={row[5]} | ts={row[6]}")

# Check a specific trade's full history
cur.execute("""
    SELECT trade_id FROM automated_signals 
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 1
""")
latest_trade = cur.fetchone()[0]

print(f"\n=== FULL HISTORY FOR {latest_trade} ===")
cur.execute("""
    SELECT event_type, be_mfe, no_be_mfe, mfe, current_price, timestamp
    FROM automated_signals 
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (latest_trade,))

for row in cur.fetchall():
    print(f"  {row[0]:15} | be_mfe={row[1]} | no_be_mfe={row[2]} | mfe={row[3]} | price={row[4]}")

conn.close()
