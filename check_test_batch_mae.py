import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check the test batch rows we just inserted
cur.execute("""
    SELECT trade_id, be_mfe, no_be_mfe, mae_global_r, timestamp
    FROM automated_signals
    WHERE trade_id IN ('20251209_100400000_BULLISH', '20251209_103900000_BULLISH')
    AND event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 5
""")

rows = cur.fetchall()
print("Test batch rows:")
for row in rows:
    print(f"{row[0]}: BE={row[1]}, NoBE={row[2]}, MAE={row[3]} @ {row[4]}")

cur.close()
conn.close()
