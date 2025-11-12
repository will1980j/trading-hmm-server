import psycopg2
import os
from datetime import datetime

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

# Check the most recent webhook received
cur.execute("""
    SELECT trade_id, event_type, direction, entry_price, timestamp,
           EXTRACT(EPOCH FROM (NOW() - timestamp)) / 60 as minutes_ago
    FROM automated_signals 
    ORDER BY timestamp DESC 
    LIMIT 5
""")

rows = cur.fetchall()

print('\n=== MOST RECENT WEBHOOKS RECEIVED ===\n')
if rows:
    for row in rows:
        trade_id, event_type, direction, entry, ts, mins_ago = row
        print(f'{trade_id}')
        print(f'  Event: {event_type}')
        print(f'  Direction: {direction}')
        print(f'  Entry: {entry}')
        print(f'  Time: {ts}')
        print(f'  Minutes ago: {mins_ago:.1f}')
        print()
else:
    print('NO WEBHOOKS RECEIVED')

cur.close()
conn.close()
