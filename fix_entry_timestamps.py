"""
Fix ENTRY timestamps in database to match trade_id timestamps.

The bug: ENTRY events were using NOW() instead of payload timestamp.
Result: Trade 20251209_215600000 (9:56 PM Dec 9) stored as 3:01 AM Dec 10.

This script extracts the correct timestamp from trade_id and updates the database.
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Find all ENTRY events where timestamp doesn't match trade_id
cur.execute("""
    SELECT id, trade_id, timestamp, signal_date, signal_time
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY id DESC
    LIMIT 100
""")

rows = cur.fetchall()
print(f"Found {len(rows)} ENTRY events to check")

fixed_count = 0
for row in rows:
    db_id, trade_id, db_timestamp, signal_date, signal_time = row
    
    # Extract timestamp from trade_id (format: YYYYMMDD_HHMMSS000_DIRECTION)
    try:
        parts = trade_id.split('_')
        if len(parts) < 2:
            print(f"  Skipping {trade_id} - invalid format")
            continue
            
        date_str = parts[0]  # YYYYMMDD
        time_str = parts[1][:6]  # HHMMSS (strip trailing 000)
        
        # Parse into datetime
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(time_str[0:2])
        minute = int(time_str[2:4])
        second = int(time_str[4:6])
        
        correct_timestamp = datetime(year, month, day, hour, minute, second)
        
        # Check if it needs fixing (allow 1 minute tolerance)
        if db_timestamp:
            diff_seconds = abs((db_timestamp - correct_timestamp).total_seconds())
            if diff_seconds < 60:
                # Already correct
                continue
        
        # Update the timestamp
        cur.execute("""
            UPDATE automated_signals
            SET timestamp = %s,
                signal_date = %s,
                signal_time = %s
            WHERE id = %s
        """, (correct_timestamp, correct_timestamp.date(), correct_timestamp.time(), db_id))
        
        print(f"  Fixed {trade_id}: {db_timestamp} → {correct_timestamp}")
        fixed_count += 1
        
    except Exception as e:
        print(f"  Error processing {trade_id}: {e}")
        continue

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Fixed {fixed_count} ENTRY timestamps")
