import psycopg2
import os
from datetime import datetime, timezone

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

# Get current time
now = datetime.now(timezone.utc)
print(f'\n=== CURRENT TIME ===')
print(f'UTC: {now}')
print(f'Timestamp: {now.timestamp()}')

# Get the most recent webhook
cur.execute("""
    SELECT trade_id, event_type, timestamp, 
           EXTRACT(EPOCH FROM timestamp) as epoch_timestamp,
           EXTRACT(EPOCH FROM (NOW() - timestamp)) as seconds_ago
    FROM automated_signals 
    ORDER BY timestamp DESC 
    LIMIT 1
""")

row = cur.fetchone()

if row:
    trade_id, event_type, ts, epoch_ts, secs_ago = row
    mins_ago = secs_ago / 60
    hours_ago = mins_ago / 60
    
    print(f'\n=== MOST RECENT WEBHOOK ===')
    print(f'Trade ID: {trade_id}')
    print(f'Event: {event_type}')
    print(f'Timestamp: {ts}')
    print(f'Epoch: {epoch_ts}')
    print(f'Seconds ago: {secs_ago:.0f}')
    print(f'Minutes ago: {mins_ago:.1f}')
    print(f'Hours ago: {hours_ago:.1f}')
else:
    print('\nNO WEBHOOKS IN DATABASE')

cur.close()
conn.close()
