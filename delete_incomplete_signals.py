import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Delete ALL rows for signals that have MFE_UPDATE but no ENTRY
cur.execute("""
    DELETE FROM automated_signals 
    WHERE trade_id IN (
        SELECT DISTINCT trade_id 
        FROM automated_signals 
        WHERE event_type = 'MFE_UPDATE'
        AND trade_id NOT IN (
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE event_type = 'ENTRY'
        )
    )
""")

deleted = cur.rowcount
conn.commit()

print(f"✅ Deleted {deleted} rows for signals without ENTRY data")

# Verify clean state
cur.execute("SELECT COUNT(DISTINCT trade_id) FROM automated_signals WHERE event_type = 'ENTRY'")
entry_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT trade_id) FROM automated_signals WHERE event_type = 'MFE_UPDATE'")
mfe_count = cur.fetchone()[0]

print(f"Clean state: {entry_count} signals with ENTRY, {mfe_count} signals with MFE_UPDATE")
print(f"All signals now have complete data!")

conn.close()
