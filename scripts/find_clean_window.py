import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
db = os.environ.get("DATABASE_URL")
if not db:
    raise SystemExit("DATABASE_URL not set")

SYMBOL = "GLBX.MDP3:NQ"
# start searching from here (UTC)
SEARCH_START = datetime(2025, 11, 30, 20, 0, tzinfo=timezone.utc)

conn = psycopg2.connect(db)
cur = conn.cursor()

def has_outlier(start, end):
    cur.execute("""
        SELECT COUNT(1)
        FROM market_bars_ohlcv_1m
        WHERE symbol=%s
          AND ts >= %s
          AND ts <= %s
          AND (low < 10000 OR high > 100000)
    """, (SYMBOL, start, end))
    return cur.fetchone()[0] > 0

def bar_count(start, end):
    cur.execute("""
        SELECT COUNT(1)
        FROM market_bars_ohlcv_1m
        WHERE symbol=%s AND ts >= %s AND ts <= %s
    """, (SYMBOL, start, end))
    return cur.fetchone()[0]

window = timedelta(minutes=60)
step = timedelta(minutes=60)

found = None
t = SEARCH_START
for _ in range(48):  # search up to 2 days
    start = t
    end = t + window
    n = bar_count(start, end)
    if n >= 50 and (not has_outlier(start, end)):
        found = (start, end, n)
        break
    t += step

cur.close(); conn.close()

if not found:
    print("NO CLEAN WINDOW FOUND in search range.")
else:
    s,e,n = found
    print("CLEAN_WINDOW_START_UTC:", s.strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("CLEAN_WINDOW_END_UTC:", e.strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("BARS:", n)
