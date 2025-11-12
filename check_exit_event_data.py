"""Check what data EXIT events actually contain"""
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

cursor.execute("""
SELECT 
    trade_id,
    event_type,
    mfe,
    be_mfe,
    no_be_mfe,
    final_mfe,
    exit_price,
    timestamp
FROM automated_signals
WHERE event_type LIKE 'EXIT_%'
ORDER BY timestamp DESC
LIMIT 10
""")

print("\n📊 Recent EXIT events:\n")
for row in cursor.fetchall():
    trade_id, event_type, mfe, be_mfe, no_be_mfe, final_mfe, exit_price, ts = row
    print(f"{trade_id} - {event_type}")
    print(f"  mfe: {mfe}")
    print(f"  be_mfe: {be_mfe}")
    print(f"  no_be_mfe: {no_be_mfe}")
    print(f"  final_mfe: {final_mfe}")
    print(f"  exit_price: {exit_price}")
    print(f"  timestamp: {ts}")
    print()

conn.close()
