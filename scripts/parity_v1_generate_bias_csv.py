#!/usr/bin/env python3
import os, sys, psycopg2, csv
from dotenv import load_dotenv
sys.path.append('.')
from services.parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

load_dotenv()

symbol = sys.argv[1] if len(sys.argv) > 1 else 'GLBX.MDP3:NQ'
start = sys.argv[2] if len(sys.argv) > 2 else '2024-01-02'
end = sys.argv[3] if len(sys.argv) > 3 else '2024-01-03'
out = sys.argv[4] if len(sys.argv) > 4 else 'python_bias.csv'

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

cursor.execute("""
    SELECT ts, open, high, low, close FROM market_bars_ohlcv_1m
    WHERE symbol = %s AND ts >= %s::timestamptz AND ts <= %s::timestamptz
    ORDER BY ts ASC
""", (symbol, start, end))

bars = cursor.fetchall()
cursor.close()
conn.close()

engine = BiasEngineFvgIfvg()

with open(out, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ts_utc', 'open', 'high', 'low', 'close', 'bias_str', 'bias_code'])
    
    for bar in bars:
        bar_dict = {'ts': bar[0], 'open': float(bar[1]), 'high': float(bar[2]), 'low': float(bar[3]), 'close': float(bar[4])}
        bias_str = engine.update(bar_dict)
        bias_code = 1 if bias_str == "Bullish" else -1 if bias_str == "Bearish" else 0
        writer.writerow([bar[0].isoformat(), bar[1], bar[2], bar[3], bar[4], bias_str, bias_code])

print(f"✅ Generated {len(bars)} bars → {out}")
