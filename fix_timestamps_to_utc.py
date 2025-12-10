"""
Convert existing timestamps from NY time to UTC.

Current problem: Timestamps are stored as NY time but treated as UTC by PostgreSQL.
Solution: Convert all timestamps to actual UTC.
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all records with timestamps
cur.execute("""
    SELECT id, trade_id, timestamp, event_type
    FROM automated_signals
    WHERE timestamp IS NOT NULL
    ORDER BY id DESC
    LIMIT 200
""")

rows = cur.fetchall()
print(f"Found {len(rows)} records to check")

fixed_count = 0
for row in rows:
    db_id, trade_id, db_timestamp, event_type = row
    
    # The timestamp is currently stored as NY time but treated as naive
    # We need to convert it to UTC by subtracting 5 hours (EST) or 4 hours (EDT)
    
    # Determine if DST was in effect (rough approximation)
    # DST in 2025: March 9 - November 2
    if db_timestamp.month >= 3 and db_timestamp.month <= 11:
        if db_timestamp.month == 3 and db_timestamp.day < 9:
            offset_hours = 5  # EST
        elif db_timestamp.month == 11 and db_timestamp.day >= 2:
            offset_hours = 5  # EST
        else:
            offset_hours = 4  # EDT
    else:
        offset_hours = 5  # EST
    
    # Convert NY time to UTC
    utc_timestamp = db_timestamp + timedelta(hours=offset_hours)
    
    # Update the timestamp
    cur.execute("""
        UPDATE automated_signals
        SET timestamp = %s
        WHERE id = %s
    """, (utc_timestamp, db_id))
    
    if fixed_count < 10:  # Show first 10
        print(f"  {trade_id} ({event_type}): {db_timestamp} → {utc_timestamp} (UTC)")
    
    fixed_count += 1

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Converted {fixed_count} timestamps to UTC")
