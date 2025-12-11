import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Signals from screenshot
signals = [
    '20251211_085500000_BEARISH',
    '20251211_084800000_BULLISH',
    '20251211_083500000_BULLISH',
    '20251211_083100000_BEARISH',
    '20251211_081700000_BEARISH',
    '20251211_080700000_BEARISH',
    '20251211_073000000_BULLISH'
]

for trade_id in signals:
    cur.execute("""
        SELECT entry_price, stop_loss 
        FROM automated_signals 
        WHERE trade_id = %s AND event_type = 'ENTRY'
    """, (trade_id,))
    
    row = cur.fetchone()
    if row:
        print(f"{trade_id}: Entry={row[0]}, Stop={row[1]}")
    else:
        print(f"{trade_id}: NO ENTRY")

cur.close()
conn.close()
