import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check both signals from screenshot
for trade_id in ['20251212_041600000_BEARISH', '20251212_041300000_BULLISH']:
    cur.execute("""
        SELECT be_mfe, no_be_mfe, mae_global_r, timestamp, data_source
        FROM automated_signals 
        WHERE trade_id = %s
        AND event_type = 'MFE_UPDATE' 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (trade_id,))

    row = cur.fetchone()
    if row:
        print(f"{trade_id} MFE data:")
        print(f"  BE MFE: {row[0]}R")
        print(f"  No-BE MFE: {row[1]}R")
        print(f"  MAE: {row[2]}R")
        print(f"  Timestamp: {row[3]}")
        print(f"  Data source: {row[4]}")
        print()
    else:
        print(f"{trade_id}: No MFE_UPDATE found")
        print()

cur.close()
conn.close()
