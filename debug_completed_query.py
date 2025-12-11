import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251210_194500000_BEARISH'

# Run the exact query from web_server.py
cur.execute("""
    WITH max_mfe AS (
        SELECT DISTINCT ON (trade_id)
            trade_id,
            be_mfe AS max_be_mfe,
            no_be_mfe AS max_no_be_mfe,
            mae_global_r AS min_mae_global_r
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
        ORDER BY trade_id, timestamp DESC
    )
    SELECT DISTINCT ON (ex.trade_id)
           ex.id,
           ex.trade_id,
           ex.event_type,
           COALESCE(en.direction, ex.direction) AS direction,
           COALESCE(en.entry_price, ex.entry_price) AS entry_price,
           COALESCE(en.stop_loss, ex.stop_loss) AS stop_loss,
           COALESCE(en.session, ex.session) AS session,
           COALESCE(en.bias, ex.bias) AS bias,
           ex.timestamp AS exit_timestamp,
           en.signal_date,
           en.signal_time,
           en.timestamp AS entry_timestamp,
           EXTRACT(EPOCH FROM (ex.timestamp - en.timestamp)) AS duration_seconds,
           COALESCE(m.max_be_mfe, 0.0) AS be_mfe,
           COALESCE(m.max_no_be_mfe, 0.0) AS no_be_mfe,
           COALESCE(m.max_no_be_mfe, 0.0) AS final_mfe,
           COALESCE(m.min_mae_global_r, 0.0) AS mae_global_r
    FROM automated_signals ex
    LEFT JOIN automated_signals en
        ON ex.trade_id = en.trade_id
        AND en.event_type = 'ENTRY'
    LEFT JOIN max_mfe m
        ON ex.trade_id = m.trade_id
    WHERE ex.event_type LIKE 'EXIT_%%'
    AND ex.trade_id = %s
    ORDER BY
        ex.trade_id,
        CASE
            WHEN ex.event_type = 'EXIT_SL' THEN 1
            WHEN ex.event_type = 'EXIT_BREAK_EVEN' THEN 2
            ELSE 3
        END,
        ex.timestamp DESC, ex.trade_id ASC
    LIMIT 1
""", (trade_id,))

row = cur.fetchone()
if row:
    print(f"Query returned {len(row)} columns:")
    print(f"  [13] be_mfe: {row[13]}")
    print(f"  [14] no_be_mfe: {row[14]}")
    print(f"  [15] final_mfe: {row[15]}")
    print(f"  [16] mae: {row[16]}")
else:
    print("No result")

cur.close()
conn.close()
