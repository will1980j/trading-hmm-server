import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db = os.environ.get("DATABASE_URL")
if not db:
    raise SystemExit("DATABASE_URL not set")

conn = psycopg2.connect(db)
cur = conn.cursor()
cur.execute("""
SELECT ts, open, high, low, close
FROM market_bars_ohlcv_1m
WHERE symbol=%s
  AND ts >= %s::timestamptz
  AND ts <= %s::timestamptz
ORDER BY ts ASC
""", ("GLBX.MDP3:NQ", "2025-11-30T23:00:00Z", "2025-11-30T23:05:00Z"))
for r in cur.fetchall():
    print(r)
cur.close(); conn.close()
