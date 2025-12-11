import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251210_194500000_BEARISH'

# Test the new query
cur.execute("""
    WITH latest_mfe AS (
        SELECT DISTINCT ON (trade_id)
            trade_id,
            timestamp AS last_mfe_ts,
            be_mfe AS latest_be_mfe,
            no_be_mfe AS latest_no_be_mfe,
            current_price AS latest_current_price,
            mae_global_r AS latest_mae_global_r
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
        ORDER BY trade_id, timestamp DESC
    )
    SELECT 
        latest_be_mfe,
        latest_no_be_mfe,
        latest_mae_global_r,
        last_mfe_ts
    FROM latest_mfe
    WHERE trade_id = %s
""", (trade_id,))

result = cur.fetchone()
if result:
    print(f"Query result for {trade_id}:")
    print(f"  BE MFE: {result[0]}")
    print(f"  No-BE MFE: {result[1]}")
    print(f"  MAE: {result[2]}")
    print(f"  Timestamp: {result[3]}")
else:
    print("No result")

cur.close()
conn.close()
