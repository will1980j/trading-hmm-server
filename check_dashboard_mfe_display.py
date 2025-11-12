"""Check what MFE values the dashboard should be displaying"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Get active trades (same query the dashboard uses)
cursor.execute("""
WITH latest_updates AS (
    SELECT DISTINCT ON (trade_id)
        trade_id,
        be_mfe,
        no_be_mfe,
        timestamp
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    ORDER BY trade_id, timestamp DESC
)
SELECT 
    s.trade_id,
    s.direction,
    s.entry_price,
    s.stop_loss,
    s.session,
    s.signal_time,
    lu.be_mfe,
    lu.no_be_mfe,
    lu.timestamp as last_update
FROM automated_signals s
LEFT JOIN latest_updates lu ON s.trade_id = lu.trade_id
WHERE s.event_type = 'SIGNAL_CREATED'
AND s.trade_id NOT IN (
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE event_type = 'EXIT_SL'
)
AND s.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY s.timestamp DESC
""")

active_trades = cursor.fetchall()

print(f"\n📊 Active Trades (Dashboard View):\n")
print(f"Total: {len(active_trades)}\n")

if len(active_trades) == 0:
    print("❌ NO ACTIVE TRADES")
    print("   This is why MFE values aren't updating - there are no active trades!")
    print("   Wait for a new signal to be created and confirmed.")
else:
    for trade in active_trades:
        print(f"Trade: {trade['trade_id']}")
        print(f"  Direction: {trade['direction']}")
        print(f"  Entry: {trade['entry_price']}, Stop: {trade['stop_loss']}")
        print(f"  Session: {trade['session']}")
        print(f"  BE MFE: {trade['be_mfe']}")
        print(f"  No BE MFE: {trade['no_be_mfe']}")
        print(f"  Last Update: {trade['last_update']}")
        print()

# Check completed trades
cursor.execute("""
SELECT 
    trade_id,
    direction,
    timestamp
FROM automated_signals
WHERE event_type = 'EXIT_SL'
AND timestamp > NOW() - INTERVAL '2 hours'
ORDER BY timestamp DESC
LIMIT 5
""")

completed = cursor.fetchall()
print(f"\n📋 Recently Completed Trades: {len(completed)}\n")
for trade in completed:
    print(f"  {trade['trade_id']} - {trade['direction']} - Completed at {trade['timestamp']}")

conn.close()
