import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check what the database thinks "today" is
cur.execute("SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP AT TIME ZONE 'America/New_York' as ny_now")
db_time = cur.fetchone()
print(f"Database UTC time: {db_time[0]}")
print(f"Database NY time: {db_time[1]}")

# Check recent entry timestamps
cur.execute("""
    SELECT 
        trade_id,
        timestamp as utc_time,
        timestamp AT TIME ZONE 'America/New_York' as ny_time,
        DATE(timestamp AT TIME ZONE 'America/New_York') as ny_date
    FROM automated_signals 
    WHERE event_type = 'ENTRY' 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

print("\nRecent ENTRY events:")
for row in cur.fetchall():
    print(f"  {row[0]}: UTC={row[1]}, NY={row[2]}, Date={row[3]}")

# Check what the calendar query returns
cur.execute("""
    SELECT 
        DATE(timestamp AT TIME ZONE 'America/New_York') as date,
        COUNT(DISTINCT trade_id) as active_count
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
    AND trade_id NOT IN (
        SELECT DISTINCT trade_id 
        FROM automated_signals 
        WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
    )
    GROUP BY DATE(timestamp AT TIME ZONE 'America/New_York')
    ORDER BY date DESC
""")

print("\nCalendar query results (active trades by date):")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} active trades")

cur.close()
conn.close()
