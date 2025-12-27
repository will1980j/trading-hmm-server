import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db = os.environ.get("DATABASE_URL")
if not db:
    raise SystemExit("DATABASE_URL not set")

START = "2025-11-30T23:24:00Z"
END   = "2025-12-01T00:19:00Z"
SYMBOL = "GLBX.MDP3:NQ"

conn = psycopg2.connect(db)
cur = conn.cursor()

cur.execute("""
SELECT MIN(low), MAX(high), COUNT(1)
FROM market_bars_ohlcv_1m
WHERE symbol = %s
  AND ts >= %s::timestamptz
  AND ts <= %s::timestamptz
""", (SYMBOL, START, END))
print("min_low, max_high, bars:", cur.fetchone())

cur.execute("""
SELECT ts, open, high, low, close
FROM market_bars_ohlcv_1m
WHERE symbol = %s
  AND (low < 10000 OR high > 100000)
  AND ts >= %s::timestamptz
  AND ts <= %s::timestamptz
ORDER BY ts ASC
LIMIT 50
""", (SYMBOL, START, END))
rows = cur.fetchall()

print("outliers:")
for r in rows:
    print(r)

cur.close()
conn.close()
