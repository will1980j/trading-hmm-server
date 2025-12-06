import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Prefer the PUBLIC Railway URL for all local diagnostics
DB_URL = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")
print("USING DB_URL =", DB_URL)

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("================================================================================")
print("QUERY 1: Table Schema")
print("================================================================================")
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'automated_signals'
    ORDER BY ordinal_position;
""")
for row in cursor.fetchall():
    print(row["column_name"], "-", row["data_type"])

print("\n================================================================================")
print("QUERY 2: Last 25 Rows")
print("================================================================================")
cursor.execute("""
    SELECT *
    FROM automated_signals
    ORDER BY id DESC
    LIMIT 25;
""")
rows = cursor.fetchall()
if not rows:
    print("No rows found (this SHOULD NOT HAPPEN in production).")
else:
    for r in rows:
        print(r)

cursor.close()
conn.close()

print("\n================================================================================")
print("DONE.")
print("================================================================================")
