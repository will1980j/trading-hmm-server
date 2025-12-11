import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

trade_id = '20251210_225700000_BULLISH'

# Get the most recent MFE_UPDATE
cur.execute("""
    SELECT timestamp, be_mfe, no_be_mfe, mae_global_r
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 1
""", (trade_id,))

row = cur.fetchone()
if row:
    ts, be_mfe, no_be_mfe, mae = row
    minutes_ago = (datetime.utcnow() - ts.replace(tzinfo=None)).total_seconds() / 60
    
    print(f"Trade: {trade_id}")
    print(f"Last update: {ts} ({minutes_ago:.1f} minutes ago)")
    print(f"  BE MFE: {be_mfe}R")
    print(f"  No-BE MFE: {no_be_mfe}R")
    print(f"  MAE: {mae}R")
    
    if minutes_ago < 2:
        print("\n✅ Recently updated! Batch is working.")
    else:
        print(f"\n⚠️ No update in {minutes_ago:.1f} minutes. Wait for next bar close.")
else:
    print("No MFE_UPDATE events found for this trade")

cur.close()
conn.close()
