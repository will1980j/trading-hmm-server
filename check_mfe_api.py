import requests
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

# Check API response
r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print("=== ACTIVE TRADES MFE VALUES (from API) ===")
for t in data.get('active_trades', []):
    print(f"Trade: {t.get('trade_id')} - be_mfe: {t.get('be_mfe')}, no_be_mfe: {t.get('no_be_mfe')}")

# Check database for MFE_UPDATE events
print("\n=== DATABASE EVENTS (last 24h) ===")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, timestamp
    FROM automated_signals
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    ORDER BY timestamp DESC
    LIMIT 30
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} - be_mfe={row[2]}, no_be_mfe={row[3]}, time={row[4]}")

cursor.close()
conn.close()
