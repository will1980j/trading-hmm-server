import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all SIGNAL_CREATED events
cur.execute("SELECT trade_id, timestamp FROM automated_signals WHERE event_type = 'SIGNAL_CREATED'")
signals = cur.fetchall()

fixed = 0
for trade_id, current_ts in signals:
    # Parse timestamp from trade_id: YYYYMMDD_HHMMSS000_DIRECTION
    parts = trade_id.split('_')
    if len(parts) >= 2:
        date_str = parts[0]  # YYYYMMDD
        time_str = parts[1][:6]  # HHMMSS
        
        # Build correct timestamp in NY timezone
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(time_str[:2])
        minute = int(time_str[2:4])
        second = int(time_str[4:6])
        
        ny_tz = ZoneInfo("America/New_York")
        correct_time_ny = datetime(year, month, day, hour, minute, second, tzinfo=ny_tz)
        correct_time_utc = correct_time_ny.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
        
        # Update timestamp
        cur.execute("""
            UPDATE automated_signals 
            SET timestamp = %s 
            WHERE trade_id = %s AND event_type = 'SIGNAL_CREATED'
        """, (correct_time_utc, trade_id))
        
        fixed += 1
        print(f"Fixed {trade_id}: {current_ts} → {correct_time_utc}")

conn.commit()
print(f"\n✅ Fixed {fixed} SIGNAL_CREATED timestamps")

conn.close()
