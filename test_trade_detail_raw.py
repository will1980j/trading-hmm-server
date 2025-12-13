"""Test trade detail with raw database query"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

trade_id = "20251212_151200000_BEARISH"

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Same query as the API
cur.execute("""
    SELECT 
        id, trade_id, event_type, direction, entry_price,
        stop_loss, session, bias, risk_distance,
        current_price, mfe, be_mfe, no_be_mfe,
        exit_price, final_mfe,
        signal_date, signal_time, timestamp
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

rows = cur.fetchall()

print(f"Trade ID: {trade_id}")
print(f"Events found: {len(rows)}")
print()

if rows:
    for i, row in enumerate(rows[:5], 1):
        print(f"Event {i}:")
        print(f"   Type: {row[2]}")
        print(f"   Timestamp: {row[17]}")
        print(f"   BE MFE: {row[11]}")
        print(f"   No-BE MFE: {row[12]}")
        print()
else:
    print("No events found!")

cur.close()
conn.close()
