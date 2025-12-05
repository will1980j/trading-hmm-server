import psycopg2
import os

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = conn.cursor()

cur.execute("""
ALTER TABLE automated_signals
ADD COLUMN IF NOT EXISTS payload_ts TIMESTAMPTZ NULL;
""")

conn.commit()
cur.close()
conn.close()

print("✅ payload_ts column added successfully")
