import requests
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Check all recent events
cursor.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, timestamp
    FROM automated_signals
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    ORDER BY timestamp DESC
    LIMIT 20
""")

print("Recent events in database:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}, be_mfe={row[2]}, no_be_mfe={row[3]}, time={row[4]}")

cursor.close()
conn.close()
