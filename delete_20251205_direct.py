#!/usr/bin/env python3
"""Delete all trades with trade_id LIKE '20251205_00%' - direct database query."""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit(1)

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# First, count matching rows
cursor.execute("""
    SELECT COUNT(*), COUNT(DISTINCT trade_id) 
    FROM automated_signals 
    WHERE trade_id LIKE '20251205_00%'
""")
row_count, trade_count = cursor.fetchone()
print(f"Found {row_count} rows across {trade_count} trades matching '20251205_00%'")

if row_count == 0:
    print("No matching rows found. Nothing to delete.")
    conn.close()
    exit(0)

# Show what we're about to delete
cursor.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE trade_id LIKE '20251205_00%'
    ORDER BY trade_id
    LIMIT 20
""")
trade_ids = cursor.fetchall()
print("\nTrade IDs to delete:")
for (tid,) in trade_ids:
    print(f"  - {tid}")

# Delete the rows
print(f"\nDeleting {row_count} rows...")
cursor.execute("""
    DELETE FROM automated_signals 
    WHERE trade_id LIKE '20251205_00%'
""")
deleted = cursor.rowcount
conn.commit()

print(f"✅ Successfully deleted {deleted} rows")

cursor.close()
conn.close()
