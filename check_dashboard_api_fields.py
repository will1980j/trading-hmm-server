import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check what the dashboard query returns
cur.execute("""
    WITH entry_data AS (
        SELECT DISTINCT ON (trade_id)
            trade_id,
            direction,
            entry_price,
            stop_loss,
            session,
            bias,
            signal_date,
            signal_time,
            timestamp as entry_timestamp
        FROM automated_signals
        WHERE event_type = 'ENTRY'
        ORDER BY trade_id, timestamp DESC
    ),
    latest_mfe AS (
        SELECT DISTINCT ON (trade_id)
            trade_id,
            mfe,
            be_mfe,
            no_be_mfe,
            current_price,
            mae_global_r,
            direction,
            session,
            timestamp as last_update
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
        ORDER BY trade_id, timestamp DESC
    ),
    active_trade_ids AS (
        SELECT DISTINCT trade_id
        FROM automated_signals
        WHERE (event_type = 'ENTRY' OR event_type = 'MFE_UPDATE')
        AND trade_id NOT IN (
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
        )
    )
    SELECT 
        a.trade_id,
        e.direction,
        e.entry_price,
        e.stop_loss,
        e.session,
        m.be_mfe,
        m.no_be_mfe,
        m.mae_global_r
    FROM active_trade_ids a
    LEFT JOIN entry_data e ON a.trade_id = e.trade_id
    LEFT JOIN latest_mfe m ON a.trade_id = m.trade_id
    WHERE m.trade_id IS NOT NULL
    ORDER BY COALESCE(e.entry_timestamp, m.last_update) DESC
""")

rows = cur.fetchall()
print(f"Query returned {len(rows)} signals:")
for row in rows:
    print(f"  {row[0]}: Entry={row[2]}, Stop={row[3]}, BE={row[5]}, NoBE={row[6]}")

# Now check without the WHERE m.trade_id IS NOT NULL filter
cur.execute("""
    WITH entry_data AS (
        SELECT DISTINCT ON (trade_id)
            trade_id,
            direction,
            entry_price,
            stop_loss,
            session
        FROM automated_signals
        WHERE event_type = 'ENTRY'
        ORDER BY trade_id, timestamp DESC
    ),
    active_trade_ids AS (
        SELECT DISTINCT trade_id
        FROM automated_signals
        WHERE event_type = 'ENTRY'
        AND trade_id NOT IN (
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
        )
    )
    SELECT 
        a.trade_id,
        e.direction,
        e.entry_price,
        e.stop_loss,
        e.session
    FROM active_trade_ids a
    LEFT JOIN entry_data e ON a.trade_id = e.trade_id
""")

rows2 = cur.fetchall()
print(f"\nWithout MFE filter: {len(rows2)} signals:")
for row in rows2:
    print(f"  {row[0]}: Entry={row[2]}, Stop={row[3]}, Session={row[4]}")

conn.close()
