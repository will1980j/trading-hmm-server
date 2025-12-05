#!/usr/bin/env python3
"""Check what December 5th trades exist."""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE trade_id LIKE '20251205%'
    ORDER BY trade_id
    LIMIT 20
""")
rows = cur.fetchall()
print(f"Found {len(rows)} trades starting with '20251205':")
for (tid,) in rows:
    print(f"  {tid}")

conn.close()
