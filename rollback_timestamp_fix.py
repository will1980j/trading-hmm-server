"""
Rollback the bad timestamp fix and convert properly to UTC.

The trade_id contains the correct NY time.
We need to convert that NY time to UTC for storage.
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all records
cur.execute("""
    SELECT id, trade_id, timestamp
    FROM automated_signals
    WHERE trade_id LIKE '202512%'
    ORDER BY id DESC
    LIMIT 100
""")

rows = cur.fetchall()
print(f"Found {len(rows)} records to fix")

fixed_count = 0
for row in rows:
    db_id, trade_id, db_timestamp = row
    
    # Extract correct timestamp from trade_id
    try:
        parts = trade_id.split('_')
        if len(parts) < 2:
            continue
            
        date_str = parts[0]  # YYYYMMDD
        time_str = parts[1][:6]  # HHMMSS
        
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(time_str[0:2])
        minute = int(time_str[2:4])
        second = int(time_str[4:6])
        
        # Create datetime in NY timezone
        ny_tz = ZoneInfo("America/New_York")
        ny_time = datetime(year, month, day, hour, minute, second, tzinfo=ny_tz)
        
        # Convert to UTC
        utc_time = ny_time.astimezone(ZoneInfo("UTC"))
        
        # Store as naive UTC (remove timezone info for storage)
        utc_naive = utc_time.replace(tzinfo=None)
        
        # Update
        cur.execute("""
            UPDATE automated_signals
            SET timestamp = %s
            WHERE id = %s
        """, (utc_naive, db_id))
        
        if fixed_count < 10:
            print(f"  {trade_id}: NY={ny_time} → UTC={utc_naive}")
        
        fixed_count += 1
        
    except Exception as e:
        print(f"  Error processing {trade_id}: {e}")
        continue

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Fixed {fixed_count} timestamps (NY → UTC)")
