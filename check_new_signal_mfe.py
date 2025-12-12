import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT be_mfe, no_be_mfe, mae_global_r, timestamp
    FROM automated_signals 
    WHERE trade_id = '20251212_040600000_BEARISH' 
    AND event_type = 'MFE_UPDATE' 
    ORDER BY timestamp DESC 
    LIMIT 1
""")

row = cur.fetchone()
if row:
    print(f"20251212_040600000_BEARISH MFE data:")
    print(f"  BE MFE: {row[0]}R")
    print(f"  No-BE MFE: {row[1]}R")
    print(f"  MAE: {row[2]}R")
    print(f"  Timestamp: {row[3]}")
else:
    print("No MFE_UPDATE found for this signal")

cur.close()
conn.close()
