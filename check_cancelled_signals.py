import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT trade_id, event_type, direction, session, timestamp 
    FROM automated_signals 
    WHERE event_type='CANCELLED' 
    ORDER BY id DESC 
    LIMIT 10
""")

rows = cur.fetchall()
if rows:
    print(f"Found {len(rows)} CANCELLED signals:")
    for r in rows:
        print(r)
else:
    print("No CANCELLED signals found in database")

cur.close()
conn.close()
