"""Check if any signals have been received recently"""
import os
import psycopg2
from datetime import datetime, timedelta

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check last 3 hours of signals
cursor.execute("""
SELECT 
    trade_id,
    event_type,
    direction,
    timestamp
FROM automated_signals
WHERE timestamp > NOW() - INTERVAL '3 hours'
ORDER BY timestamp DESC
LIMIT 20
""")

rows = cursor.fetchall()

print(f"\n📊 Signals received in last 3 hours: {len(rows)}\n")

if len(rows) == 0:
    print("❌ NO SIGNALS RECEIVED!")
    print("   The indicator is not sending webhooks")
    print("   Check:")
    print("   1. Is the indicator running in TradingView?")
    print("   2. Did the indicator update break something?")
    print("   3. Are there any compilation errors?")
else:
    print("Recent signals:\n")
    for row in rows:
        trade_id, event_type, direction, ts = row
        minutes_ago = (datetime.now() - ts.replace(tzinfo=None)).total_seconds() / 60
        dir_str = direction if direction else "N/A"
        print(f"  {trade_id} - {event_type:15} - {dir_str:8} - {minutes_ago:.1f} min ago")
    
    # Check last ENTRY event
    cursor.execute("""
    SELECT trade_id, timestamp
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 1
    """)
    
    last_entry = cursor.fetchone()
    if last_entry:
        trade_id, ts = last_entry
        minutes_ago = (datetime.now() - ts.replace(tzinfo=None)).total_seconds() / 60
        print(f"\n⏰ Last ENTRY event: {trade_id}")
        print(f"   {minutes_ago:.1f} minutes ago")
        
        if minutes_ago > 120:
            print(f"   ⚠️ No new signals in {minutes_ago/60:.1f} hours!")

conn.close()
