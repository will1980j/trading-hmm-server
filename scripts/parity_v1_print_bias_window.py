#!/usr/bin/env python3
import os, sys, psycopg2
from datetime import datetime, time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

if len(sys.argv) < 4:
    print("Usage: python scripts/parity_v1_print_bias_window.py SYMBOL START_DATE END_DATE WARMUP")
    print("Example: python scripts/parity_v1_print_bias_window.py GLBX.MDP3:NQ 2024-01-02 2024-01-03 5")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
warmup = max(0, int(sys.argv[4])) if len(sys.argv) > 4 else 5

# Parse dates to UTC with proper time boundaries
utc_tz = ZoneInfo('UTC')

if 'T' in start_date:
    start_ts = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
else:
    start_ts = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)

if 'T' in end_date:
    end_ts = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
else:
    end_ts = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=utc_tz)

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

cursor.execute("""
    SELECT ts, open, high, low, close FROM market_bars_ohlcv_1m
    WHERE symbol = %s AND ts >= %s AND ts <= %s
    ORDER BY ts ASC
""", (symbol, start_ts, end_ts))

bars = cursor.fetchall()
cursor.close()
conn.close()

if len(bars) < 3:
    print(f"WARNING: Not enough bars to evaluate (need >= 3 for FVG). Found: {len(bars)}")
    sys.exit(0)

engine = BiasEngineFvgIfvg()

print(f"{'TS':<20} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8} {'Bias':<10} BullFVG BearFVG BullIFVG BearIFVG")
print("-" * 100)

start_index = min(warmup, max(0, len(bars) - 1))

for i, bar in enumerate(bars):
    bar_dict = {'ts': bar[0], 'open': float(bar[1]), 'high': float(bar[2]), 'low': float(bar[3]), 'close': float(bar[4])}
    bias = engine.update(bar_dict)
    
    if i < start_index:
        continue
    
    print(f"{bar[0].isoformat():<20} {bar[1]:>8.2f} {bar[2]:>8.2f} {bar[3]:>8.2f} {bar[4]:>8.2f} {bias:<10} {len(engine.bull_fvg_highs):>7} {len(engine.bear_fvg_highs):>7} {len(engine.bull_ifvg_highs):>8} {len(engine.bear_ifvg_highs):>8}")

displayed = max(0, len(bars) - start_index)
print(f"\nProcessed {len(bars)} bars (displayed {displayed} after warmup of {warmup})")
