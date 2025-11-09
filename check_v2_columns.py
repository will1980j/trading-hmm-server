import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cursor = conn.cursor()

cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'signal_lab_v2_trades'
    ORDER BY ordinal_position
""")

print("signal_lab_v2_trades columns:")
print("=" * 50)
for row in cursor.fetchall():
    print(f"{row['column_name']}: {row['data_type']}")

cursor.close()
conn.close()
