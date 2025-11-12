"""Check MFE values in automated_signals table"""
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get recent signals with their MFE values
cursor.execute("""
SELECT 
    trade_id,
    event_type,
    direction,
    entry_price,
    stop_loss,
    mfe,
    be_mfe,
    no_be_mfe,
    timestamp
FROM automated_signals
WHERE event_type IN ('SIGNAL_CREATED', 'MFE_UPDATE', 'EXIT_SL')
ORDER BY timestamp DESC
LIMIT 30
""")

print("\n📊 Recent Automated Signals:\n")
for row in cursor.fetchall():
    trade_id, event_type, direction, entry, stop, mfe, be_mfe, no_be_mfe, ts = row
    dir_str = direction if direction else "N/A"
    entry_str = f"{entry}" if entry else "N/A"
    stop_str = f"{stop}" if stop else "N/A"
    mfe_str = f"{mfe}" if mfe else "N/A"
    be_mfe_str = f"{be_mfe}" if be_mfe else "N/A"
    no_be_mfe_str = f"{no_be_mfe}" if no_be_mfe else "N/A"
    
    print(f"{trade_id} | {event_type:15} | {dir_str:8}")
    print(f"  Entry:{entry_str} Stop:{stop_str}")
    print(f"  MFE:{mfe_str} BE_MFE:{be_mfe_str} NO_BE_MFE:{no_be_mfe_str}")
    print(f"  Time: {ts}")
    print()

conn.close()
