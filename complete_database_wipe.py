"""Complete database wipe - delete ALL signal data"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("Deleting ALL signal data...")
cur.execute("DELETE FROM automated_signals")
deleted = cur.rowcount
conn.commit()

print(f"✅ Deleted {deleted} rows")
print("Database completely wiped")

cur.close()
conn.close()
