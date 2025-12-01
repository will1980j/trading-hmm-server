#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

load_dotenv()
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Check for Dec 1 data
print("Looking for Dec 1 2025 data...")
cur.execute("""
    SELECT * FROM automated_signals 
    WHERE timestamp >= '2025-12-01' 
    ORDER BY timestamp DESC
""")
cols = [desc[0] for desc in cur.description]
rows = cur.fetchall()
print(f"Found {len(rows)} rows from Dec 1")

for row in rows:
    print(dict(zip(cols, row)))
    print()

# Also check trade_ids that match the chart (05:22 and 05:27)
print("\n\nLooking for trade_ids with 0522 or 0527...")
cur.execute("""
    SELECT * FROM automated_signals 
    WHERE trade_id LIKE '%0522%' OR trade_id LIKE '%0527%'
    ORDER BY timestamp DESC
""")
rows = cur.fetchall()
print(f"Found {len(rows)} matching rows")
for row in rows:
    print(dict(zip(cols, row)))

cur.close()
conn.close()
