#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Search for the specific trade_ids from the API
print("Looking for specific trade_ids...")
cur.execute("""
    SELECT * FROM automated_signals 
    WHERE trade_id IN ('20251201_052800000_BEARISH', '20251201_052400000_BULLISH')
""")
cols = [desc[0] for desc in cur.description]
rows = cur.fetchall()
print(f"Found {len(rows)} rows")
for row in rows:
    print(dict(zip(cols, row)))
    print()

# Check most recent entries by ID
print("\n\nMost recent by ID...")
cur.execute("SELECT * FROM automated_signals ORDER BY id DESC LIMIT 5")
for row in cur.fetchall():
    print(dict(zip(cols, row)))
    print()

# Check total count
cur.execute("SELECT COUNT(*) FROM automated_signals")
print(f"\nTotal rows in table: {cur.fetchone()[0]}")

# Check max timestamp
cur.execute("SELECT MAX(timestamp) FROM automated_signals")
print(f"Max timestamp: {cur.fetchone()[0]}")

cur.close()
conn.close()
