#!/usr/bin/env python3
"""
Print HTF bias window for visual parity checks
Shows 1M bias + all HTF biases per bar
"""

import os, sys, psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg
from market_parity.htf_bias import HTFBiasEngine

if len(sys.argv) < 4:
    print("Usage: python scripts/parity_v1_print_htf_bias_window.py SYMBOL START_DATE END_DATE WARMUP")
    print("Example: python scripts/parity_v1_print_htf_bias_window.py GLBX.MDP3:NQ 2024-01-02 2024-01-03 5")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
warmup = max(0, int(sys.argv[4])) if len(sys.argv) > 4 else 5

# Parse dates to UTC
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
    print(f"WARNING: Not enough bars (need >= 3 for FVG). Found: {len(bars)}")
    sys.exit(0)

# Initialize engines
bias_1m_engine = BiasEngineFvgIfvg()
htf_engine = HTFBiasEngine()

print(f"{'TS':<20} {'Close':>8} {'1M':<10} {'5M':<10} {'15M':<10} {'1H':<10} {'4H':<10} {'Daily':<10}")
print("-" * 100)

start_index = min(warmup, max(0, len(bars) - 1))

for i, bar in enumerate(bars):
    bar_dict = {
        'ts': bar[0],
        'open': float(bar[1]),
        'high': float(bar[2]),
        'low': float(bar[3]),
        'close': float(bar[4])
    }
    
    # Update both engines
    bias_1m = bias_1m_engine.update(bar_dict)
    htf_biases = htf_engine.update_ltf_bar(bar_dict)
    
    if i < start_index:
        continue
    
    print(f"{bar[0].isoformat():<20} {bar[4]:>8.2f} {bias_1m:<10} {htf_biases['m5_bias']:<10} {htf_biases['m15_bias']:<10} {htf_biases['h1_bias']:<10} {htf_biases['h4_bias']:<10} {htf_biases['daily_bias']:<10}")

displayed = max(0, len(bars) - start_index)
print(f"\nProcessed {len(bars)} bars (displayed {displayed} after warmup of {warmup})")
