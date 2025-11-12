"""Check what event types exist in the database"""
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

cursor.execute("""
SELECT DISTINCT event_type, COUNT(*) as count
FROM automated_signals
GROUP BY event_type
ORDER BY count DESC
""")

print("\n📊 Event Types in Database:\n")
for row in cursor.fetchall():
    event_type, count = row
    print(f"  {event_type}: {count} records")

conn.close()
