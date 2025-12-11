import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251210_194500000_BEARISH'

# Test just the CTE
cur.execute("""
    SELECT DISTINCT ON (trade_id)
        trade_id,
        be_mfe AS max_be_mfe,
        no_be_mfe AS max_no_be_mfe,
        mae_global_r AS min_mae_global_r,
        timestamp
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND trade_id = %s
    ORDER BY trade_id, timestamp DESC
    LIMIT 1
""", (trade_id,))

row = cur.fetchone()
if row:
    print(f"CTE result for {trade_id}:")
    print(f"  BE MFE: {row[1]}")
    print(f"  No-BE MFE: {row[2]}")
    print(f"  MAE: {row[3]}")
    print(f"  Timestamp: {row[4]}")
else:
    print("No result from CTE")

cur.close()
conn.close()
