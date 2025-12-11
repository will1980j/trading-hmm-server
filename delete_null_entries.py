import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Delete ENTRY rows with NULL entry_price (the bad ones we just created)
cur.execute("""
    DELETE FROM automated_signals
    WHERE event_type = 'ENTRY'
    AND entry_price IS NULL
    RETURNING trade_id
""")

deleted = cur.fetchall()
print(f"Deleted {len(deleted)} NULL ENTRY rows:")
for row in deleted:
    print(f"  {row[0]}")

conn.commit()
cur.close()
conn.close()
