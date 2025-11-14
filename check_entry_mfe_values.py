import psycopg2
import os
from datetime import datetime

# Get database connection
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get the most recent ENTRY event
cursor.execute("""
    SELECT 
        trade_id,
        event_type,
        be_mfe,
        no_be_mfe,
        entry_price,
        stop_loss,
        risk_distance,
        timestamp
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 5
""")

results = cursor.fetchall()

print("\n" + "="*80)
print("MOST RECENT ENTRY EVENTS - RAW DATABASE VALUES")
print("="*80)

for row in results:
    trade_id, event_type, be_mfe, no_be_mfe, entry_price, stop_loss, risk_distance, timestamp = row
    print(f"\nTrade ID: {trade_id}")
    print(f"Event Type: {event_type}")
    print(f"BE MFE (database): {be_mfe}")
    print(f"No BE MFE (database): {no_be_mfe}")
    print(f"Entry Price: {entry_price}")
    print(f"Stop Loss: {stop_loss}")
    print(f"Risk Distance: {risk_distance}")
    print(f"Timestamp: {timestamp}")
    print("-" * 80)

cursor.close()
conn.close()

print("\n✅ Check complete")
print("\nIf MFE values are 0.00 in database but showing 2.952 in dashboard,")
print("then the dashboard is CALCULATING MFE instead of displaying database values!")
