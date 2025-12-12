import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Delete MFE_UPDATE rows for signals from before Dec 12
cur.execute("""
    DELETE FROM automated_signals 
    WHERE event_type = 'MFE_UPDATE' 
    AND trade_id < '20251212_000000000'
""")

deleted = cur.rowcount
conn.commit()

print(f"✅ Deleted {deleted} old MFE_UPDATE rows from before Dec 12")

# Verify what's left
cur.execute("SELECT COUNT(DISTINCT trade_id) FROM automated_signals WHERE event_type = 'ENTRY'")
entry_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT trade_id) FROM automated_signals WHERE event_type = 'MFE_UPDATE'")
mfe_count = cur.fetchone()[0]

print(f"Remaining signals: {entry_count} with ENTRY, {mfe_count} with MFE_UPDATE")

conn.close()
