#!/usr/bin/env python3
"""
Print signal generation window for visual parity checks
Shows bias, HTF biases, alignment, engulfing, and triangle signals
"""

import os, sys, psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg
from market_parity.htf_bias import HTFBiasEngine
from market_parity.htf_alignment import compute_htf_alignment
from market_parity.engulfing import Bar, detect_engulfing
from market_parity.signal_generation import generate_signals

if len(sys.argv) < 4:
    print("Usage: python scripts/parity_v1_print_signal_window.py SYMBOL START_DATE END_DATE WARMUP")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
warmup = max(0, int(sys.argv[4])) if len(sys.argv) > 4 else 5

# Parse dates
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
    print(f"WARNING: Not enough bars. Found: {len(bars)}")
    sys.exit(0)

# Initialize engines
bias_engine = BiasEngineFvgIfvg()
htf_engine = HTFBiasEngine()

# Filter settings (default: all off)
use_flags = {'daily': False, 'h4': False, 'h1': False, 'm15': False, 'm5': False}
htf_aligned_only = False
require_engulfing = False
require_sweep_engulfing = False

print(f"{'TS':<20} {'Bias':<10} {'HTF_B':<6} {'HTF_R':<6} {'Eng':<4} {'Swp':<4} {'Bull':<5} {'Bear':<5}")
print("-" * 80)

bias_prev = "Neutral"
prev_bar = None

start_index = min(warmup, max(0, len(bars) - 1))

for i, bar_tuple in enumerate(bars):
    bar_dict = {
        'ts': bar_tuple[0],
        'open': float(bar_tuple[1]),
        'high': float(bar_tuple[2]),
        'low': float(bar_tuple[3]),
        'close': float(bar_tuple[4])
    }
    
    # Update bias
    bias = bias_engine.update(bar_dict)
    
    # Update HTF biases
    htf_biases = htf_engine.update_ltf_bar(bar_dict)
    
    # Compute HTF alignment
    biases_dict = {
        'daily': htf_biases['daily_bias'],
        'h4': htf_biases['h4_bias'],
        'h1': htf_biases['h1_bias'],
        'm15': htf_biases['m15_bias'],
        'm5': htf_biases['m5_bias']
    }
    htf_bull, htf_bear = compute_htf_alignment(biases_dict, use_flags)
    
    # Detect engulfing
    if prev_bar is not None:
        prev_bar_obj = Bar(prev_bar['open'], prev_bar['high'], prev_bar['low'], prev_bar['close'])
        curr_bar_obj = Bar(bar_dict['open'], bar_dict['high'], bar_dict['low'], bar_dict['close'])
        engulfing = detect_engulfing(prev_bar_obj, curr_bar_obj)
    else:
        engulfing = None
    
    # Generate signals
    if engulfing is not None:
        signals = generate_signals(
            bias=bias,
            bias_prev=bias_prev,
            htf_bullish=htf_bull,
            htf_bearish=htf_bear,
            bullish_engulfing=engulfing.bullish,
            bearish_engulfing=engulfing.bearish,
            bullish_sweep_engulfing=engulfing.bullish_sweep,
            bearish_sweep_engulfing=engulfing.bearish_sweep,
            htf_aligned_only=htf_aligned_only,
            require_engulfing=require_engulfing,
            require_sweep_engulfing=require_sweep_engulfing
        )
        
        if i >= start_index:
            eng_str = "BE" if engulfing.bullish or engulfing.bearish else "--"
            swp_str = "SW" if engulfing.bullish_sweep or engulfing.bearish_sweep else "--"
            bull_str = "BULL" if signals['show_bull_triangle'] else ""
            bear_str = "BEAR" if signals['show_bear_triangle'] else ""
            
            print(f"{bar_tuple[0].isoformat():<20} {bias:<10} {str(htf_bull)[0]:<6} {str(htf_bear)[0]:<6} {eng_str:<4} {swp_str:<4} {bull_str:<5} {bear_str:<5}")
    
    # Update for next iteration
    bias_prev = bias
    prev_bar = bar_dict

displayed = max(0, len(bars) - start_index)
print(f"\nProcessed {len(bars)} bars (displayed {displayed} after warmup of {warmup})")
