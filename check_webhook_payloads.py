import psycopg2
import os
import json

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

# Get the most recent trades with ALL their events
cur.execute("""
    SELECT trade_id, event_type, timestamp, 
           be_mfe, no_be_mfe,
           EXTRACT(EPOCH FROM timestamp) as epoch_time
    FROM automated_signals 
    WHERE signal_date = CURRENT_DATE
    ORDER BY timestamp DESC
    LIMIT 30
""")

rows = cur.fetchall()

print('\n=== RECENT WEBHOOK EVENTS (MOST RECENT FIRST) ===\n')

current_trade = None
trade_events = {}

for row in rows:
    trade_id, event_type, timestamp, be_mfe, no_be_mfe, epoch_time = row
    
    if trade_id not in trade_events:
        trade_events[trade_id] = []
    
    trade_events[trade_id].append({
        'event': event_type,
        'timestamp': timestamp,
        'be_mfe': float(be_mfe) if be_mfe else 0.0,
        'no_be_mfe': float(no_be_mfe) if no_be_mfe else 0.0,
        'epoch': epoch_time
    })

# Now print organized by trade
for trade_id, events in trade_events.items():
    print(f'\n{trade_id}:')
    
    # Calculate duration between first and last event
    if len(events) > 1:
        first_epoch = events[-1]['epoch']  # Last in list (oldest)
        last_epoch = events[0]['epoch']    # First in list (newest)
        duration = last_epoch - first_epoch
        print(f'  Duration: {duration:.1f} seconds')
    
    # Print events in chronological order (reverse)
    for event in reversed(events):
        print(f'  {event["timestamp"]} | {event["event"]:<20} | BE: {event["be_mfe"]:.2f}R | No BE: {event["no_be_mfe"]:.2f}R')

cur.close()
conn.close()
