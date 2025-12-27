import os
import psycopg2
from dotenv import load_dotenv
from datetime import timezone
from pathlib import Path
import sys

# repo root import
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from services.parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

load_dotenv()
db = os.environ.get("DATABASE_URL")
if not db:
    raise SystemExit("DATABASE_URL not set")

SYMBOL = "GLBX.MDP3:NQ"

# TradingView UTC-5 times you care about:
# 18:23–18:25 UTC-5  =>  23:23–23:25 UTC
START = "2025-11-30T23:23:00Z"
END   = "2025-11-30T23:25:00Z"

conn = psycopg2.connect(db)
cur = conn.cursor()
cur.execute("""
SELECT ts, open, high, low, close
FROM market_bars_ohlcv_1m
WHERE symbol=%s
  AND ts >= %s::timestamptz
  AND ts <= %s::timestamptz
ORDER BY ts ASC
""", (SYMBOL, START, END))
rows = cur.fetchall()
cur.close(); conn.close()

print("DB_OHLC:")
for r in rows:
    print(r)

# Now compute bias codes, but IMPORTANT:
# we must warm up from the first available bar in this session window.
# We'll warm from 23:00Z to 23:25Z and print 23:23–23:25 outputs.
WARM_START = "2025-11-30T23:00:00Z"
WARM_END   = "2025-11-30T23:25:00Z"

conn = psycopg2.connect(db)
cur = conn.cursor()
cur.execute("""
SELECT ts, open, high, low, close
FROM market_bars_ohlcv_1m
WHERE symbol=%s
  AND ts >= %s::timestamptz
  AND ts <= %s::timestamptz
ORDER BY ts ASC
""", (SYMBOL, WARM_START, WARM_END))
warm_rows = cur.fetchall()
cur.close(); conn.close()

eng = BiasEngineFvgIfvg()
print("\nPY_BIAS (ts_utc,bias_code,bias_str):")
for ts,o,h,l,c in warm_rows:
    bias = eng.update({"ts": ts, "open": float(o), "high": float(h), "low": float(l), "close": float(c)})
    code = 1 if bias=="Bullish" else (-1 if bias=="Bearish" else 0)
    if ts.isoformat().startswith("2025-11-30T23:23") or ts.isoformat().startswith("2025-11-30T23:24") or ts.isoformat().startswith("2025-11-30T23:25"):
        print(ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), code, bias)
