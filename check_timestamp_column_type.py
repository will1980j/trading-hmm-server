import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type, datetime_precision
    FROM information_schema.columns 
    WHERE table_name = 'automated_signals' 
    AND column_name = 'timestamp'
""")

result = cur.fetchone()
print(f"Column: {result[0]}")
print(f"Data type: {result[1]}")
print(f"Precision: {result[2]}")

cur.close()
conn.close()
