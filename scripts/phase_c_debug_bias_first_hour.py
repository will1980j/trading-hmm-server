#!/usr/bin/env python3
"""Debug bias for first hour of Pine history"""

import os, sys, psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

load_dotenv()

symbol = 'GLBX.MDP3:NQ'
start_ts = datetime.fromisoformat('2025-11-30T23:00:00+00:00')
end_ts = datetime.fromisoformat('2025-12-01T00:00:00+00:00')

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

engine = BiasEngineFvgIfvg()

print(f"Bias sanity check: {start_ts.isoformat()} to {end_ts.isoformat()}")
print(f"{'UTC':<20} {'TV (UTC-5)':<20} {'Close':>8} {'Bias':<10}")
print("-" * 70)

for bar in bars:
    bar_dict = {'ts': bar[0], 'open': float(bar[1]), 'high': float(bar[2]), 'low': float(bar[3]), 'close': float(bar[4])}
    bias = engine.update(bar_dict)
    
    # Convert to TV time (UTC-5)
    tv_time = bar[0].astimezone(ZoneInfo('America/New_York'))
    
    print(f"{bar[0].isoformat():<20} {tv_time.strftime('%Y-%m-%d %H:%M'):<20} {bar[4]:>8.2f} {bias:<10}")

print(f"\nExpected:")
print("  - Neutral at start")
print("  - Bullish at TV 18:24 (UTC 23:24)")
print("  - Bearish at TV 18:26 (UTC 23:26)")
