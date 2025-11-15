import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get a sample trade_id
cursor.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    LIMIT 1
""")
trade_id = cursor.fetchone()[0]
print(f"Testing with trade_id: {trade_id}")

# Test the exact query from the endpoint
cursor.execute("""
    SELECT 
        id, trade_id, event_type, direction, entry_price, stop_loss,
        risk_distance, be_mfe, no_be_mfe, session, bias,
        signal_date, signal_time, timestamp
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

print(f"\nColumn names: {[desc[0] for desc in cursor.description]}")
print(f"\nNumber of rows: {cursor.rowcount}")

rows = cursor.fetchall()
for i, row in enumerate(rows[:3]):
    print(f"\nRow {i+1}:")
    for j, col in enumerate(cursor.description):
        print(f"  {col[0]}: {row[j]}")

cursor.close()
conn.close()
