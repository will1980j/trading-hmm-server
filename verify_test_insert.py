#!/usr/bin/env python3
"""Verify the test data was inserted"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check for the test trade
print("=== CHECKING FOR TEST TRADE ===")
cur.execute("""
    SELECT id, trade_id, event_type, direction, entry_price, timestamp
    FROM automated_signals 
    WHERE trade_id LIKE 'TEST_%'
    ORDER BY timestamp DESC
""")
for row in cur.fetchall():
    print(f"  ID={row[0]}, trade={row[1]}, type={row[2]}, dir={row[3]}, entry={row[4]}, ts={row[5]}")

# Check most recent entries
print("\n=== MOST RECENT ENTRIES (after test) ===")
cur.execute("""
    SELECT id, trade_id, event_type, timestamp
    FROM automated_signals 
    ORDER BY id DESC
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  ID={row[0]}, trade={row[1]}, type={row[2]}, ts={row[3]}")

# Clean up test data
print("\n=== CLEANING UP TEST DATA ===")
cur.execute("DELETE FROM automated_signals WHERE trade_id LIKE 'TEST_%'")
deleted = cur.rowcount
conn.commit()
print(f"  Deleted {deleted} test records")

cur.close()
conn.close()
