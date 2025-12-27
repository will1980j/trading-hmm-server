import os
import sys
import argparse
import psycopg2
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on sys.path so "services.*" imports work
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from services.parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

def parse_ts(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s).astimezone(timezone.utc)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    args = ap.parse_args()

    db = os.environ.get("DATABASE_URL")
    if not db:
        raise SystemExit("DATABASE_URL not set")

    start_utc = parse_ts(args.start)
    end_utc = parse_ts(args.end)

    conn = psycopg2.connect(db)
    cur = conn.cursor()
    cur.execute("""
        SELECT ts, open, high, low, close
        FROM market_bars_ohlcv_1m
        WHERE symbol = %s
          AND ts >= %s
          AND ts <= %s
        ORDER BY ts ASC
    """, (args.symbol, start_utc, end_utc))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("NO BARS RETURNED for that window.")
        return

    eng = BiasEngineFvgIfvg()

    print("ts_utc,open,high,low,close,bias_code,bias_str")
    for ts, o, h, l, c in rows:
        bar = {"ts": ts, "open": float(o), "high": float(h), "low": float(l), "close": float(c)}
        bias = eng.update(bar)
        code = 1 if bias == "Bullish" else (-1 if bias == "Bearish" else 0)
        ts_iso = ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"{ts_iso},{bar['open']},{bar['high']},{bar['low']},{bar['close']},{code},{bias}")

if __name__ == "__main__":
    main()
