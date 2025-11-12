"""Check automated_signals table schema"""
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

cursor.execute("""
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'automated_signals'
ORDER BY ordinal_position
""")

print("\n📋 automated_signals table columns:\n")
for col in cursor.fetchall():
    print(f"  {col[0]}: {col[1]}")

conn.close()
