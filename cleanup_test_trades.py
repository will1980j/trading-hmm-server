"""Clean up test trades from the database"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:lfBgPBxCMdqwsnLzLXHnuKQCkXAOqZjq@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Delete test trades
cursor.execute("""
    DELETE FROM automated_signals 
    WHERE trade_id LIKE 'TEST_%' 
    OR trade_id LIKE 'DIRECT_TEST_%'
""")

deleted = cursor.rowcount
conn.commit()
print(f"Deleted {deleted} test trade records")

cursor.close()
conn.close()
