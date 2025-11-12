"""
Cleanup script for stuck ACTIVE trades that never received completion webhooks
Marks trades as completed if they're more than 2 hours old without an EXIT event
"""
import os
import psycopg2
from datetime import datetime, timedelta

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Find all ENTRY events without corresponding EXIT events that are > 2 hours old
cursor.execute("""
SELECT 
    e.trade_id,
    e.direction,
    e.timestamp,
    e.entry_price,
    e.stop_loss
FROM automated_signals e
WHERE e.event_type = 'ENTRY'
AND e.timestamp < NOW() - INTERVAL '2 hours'
AND e.trade_id NOT IN (
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE event_type LIKE 'EXIT_%'
)
ORDER BY e.timestamp DESC
""")

stuck_trades = cursor.fetchall()

print(f"\n🔍 Found {len(stuck_trades)} stuck trades older than 2 hours\n")

if len(stuck_trades) == 0:
    print("✅ No stuck trades to clean up!")
    conn.close()
    exit(0)

print("These trades will be marked as completed with EXIT_STOP_LOSS:\n")
for trade in stuck_trades:
    trade_id, direction, timestamp, entry, stop = trade
    age_hours = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds() / 3600
    print(f"  {trade_id} - {direction} - {age_hours:.1f} hours old")

response = input(f"\n❓ Mark these {len(stuck_trades)} trades as completed? (yes/no): ")

if response.lower() != 'yes':
    print("❌ Cleanup cancelled")
    conn.close()
    exit(0)

# Insert EXIT_STOP_LOSS events for all stuck trades
completed_count = 0
for trade in stuck_trades:
    trade_id, direction, timestamp, entry, stop = trade
    
    try:
        # Insert EXIT_STOP_LOSS event with final_mfe = 0 (since we don't know the actual MFE)
        cursor.execute("""
        INSERT INTO automated_signals (
            trade_id, 
            event_type, 
            final_mfe,
            timestamp
        ) VALUES (%s, %s, %s, NOW())
        """, (trade_id, 'EXIT_STOP_LOSS', 0.0))
        
        completed_count += 1
        print(f"  ✅ {trade_id} marked as completed")
        
    except Exception as e:
        print(f"  ❌ {trade_id} failed: {e}")

conn.commit()
conn.close()

print(f"\n✅ Cleanup complete! Marked {completed_count} trades as completed")
print(f"   These trades will now show as COMPLETED on the dashboard")
