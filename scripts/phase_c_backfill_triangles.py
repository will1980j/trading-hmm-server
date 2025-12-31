#!/usr/bin/env python3
"""
Phase C Stage 1: Backfill Triangle Events
Generate historical triangle signals from Databento OHLCV using Phase B modules
"""

import os, sys, psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import subprocess

sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg
from market_parity.htf_bias import HTFBiasEngine
from market_parity.htf_alignment import compute_htf_alignment
from market_parity.engulfing import Bar, detect_engulfing
from market_parity.signal_generation import generate_signals

# Bar interval for timestamp conversion
BAR_INTERVAL = timedelta(minutes=1)

# Debug mode - set DEBUG_TS environment variable to enable
DEBUG_TS = os.environ.get('DEBUG_TS')
debug_target_ts = None
if DEBUG_TS:
    debug_target_ts = datetime.fromisoformat(DEBUG_TS.replace('Z', '+00:00'))

# Get logic version (git hash or passed version)
try:
    logic_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                           stderr=subprocess.DEVNULL).decode().strip()
except:
    logic_version = os.environ.get('LOGIC_VERSION', 'unknown')

if len(sys.argv) < 4:
    print("Usage: python scripts/phase_c_backfill_triangles.py SYMBOL START_DATE END_DATE WARMUP [PRELOAD_START_TS]")
    print("Example: python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z")
    print("\nEnvironment:")
    print("  PURGE=1  Delete existing triangles in date range before backfill")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
warmup = max(0, int(sys.argv[4])) if len(sys.argv) > 4 else 5
preload_start_ts_arg = sys.argv[5] if len(sys.argv) > 5 else "2025-11-30T23:00:00Z"

# Parse dates to UTC
utc_tz = ZoneInfo('UTC')

# Compute insert window in OPEN time
if 'T' in start_date:
    insert_open_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
else:
    insert_open_start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)

if 'T' in end_date:
    insert_open_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
else:
    insert_open_end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=utc_tz)

# Compute fetch window (need CLOSE bars to generate OPEN timestamps)
insert_close_end = insert_open_end + BAR_INTERVAL

# Parse preload start timestamp
preload_start_ts = datetime.fromisoformat(preload_start_ts_arg.replace("Z", "+00:00"))

print(f"Phase C Stage 1: Triangle Backfill")
print(f"Symbol: {symbol}")
print(f"Insert range: {start_date} to {end_date}")
print(f"Preload: from {preload_start_ts_arg}")
print(f"Warmup: {warmup} bars")
print("-" * 80)

# Connect to database
print("Connecting to database...")
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# PURGE if requested
if os.environ.get("PURGE") == "1":
    print(f"PURGE=1 detected - deleting existing triangles in insert range...")
    # triangle_events_v1.ts stores bar OPEN time (TradingView timestamp)
    cursor.execute("""
        DELETE FROM triangle_events_v1
        WHERE symbol = %s AND ts >= %s AND ts <= %s
    """, (symbol, insert_open_start, insert_open_end))
    deleted = cursor.rowcount
    conn.commit()
    print(f"Deleted {deleted} existing rows")

# Check if clean table exists and has data for this range
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'market_bars_ohlcv_1m_clean'
    )
""")
clean_table_exists = cursor.fetchone()[0]

use_clean_table = False
if clean_table_exists:
    cursor.execute("""
        SELECT COUNT(*) FROM market_bars_ohlcv_1m_clean
        WHERE symbol = %s AND ts >= %s AND ts <= %s
    """, (symbol, preload_start_ts, insert_close_end))
    clean_count = cursor.fetchone()[0]
    if clean_count > 0:
        use_clean_table = True
        print(f"Using clean OHLCV table (found {clean_count} bars in range)")

# Phase D.0: Disallow legacy table unless --allow-legacy flag is set
allow_legacy = '--allow-legacy' in sys.argv
if not use_clean_table and not allow_legacy:
    print("ERROR: Clean table not available for this range")
    print("  Clean table is required for Phase D.0+")
    print("  To use legacy table, pass --allow-legacy flag (not recommended)")
    cursor.close()
    conn.close()
    sys.exit(1)

# Determine timestamp semantics based on table
# Clean table: ts = bar OPEN time (matches TradingView)
# Legacy table: ts = bar CLOSE time (Databento default)
ts_is_open_time = use_clean_table

# Fetch bars (preload range to insert end)
table_name = 'market_bars_ohlcv_1m_clean' if use_clean_table else 'market_bars_ohlcv_1m'
print(f"Fetching OHLCV bars from {preload_start_ts.date()} to {insert_close_end.date()} (table: {table_name})...")
print(f"Timestamp semantics: ts = bar {'OPEN' if ts_is_open_time else 'CLOSE'} time")
print(f"Logic version: {logic_version}")
cursor.execute(f"""
    SELECT ts, open, high, low, close FROM {table_name}
    WHERE symbol = %s AND ts >= %s AND ts <= %s
    ORDER BY ts ASC
""", (symbol, preload_start_ts, insert_close_end))

bars = cursor.fetchall()
print(f"Fetched {len(bars)} bars (includes preload from {preload_start_ts_arg})")

if len(bars) < 3:
    print(f"ERROR: Not enough bars (need >= 3 for FVG). Found: {len(bars)}")
    cursor.close()
    conn.close()
    sys.exit(1)

# Initialize engines
print("Initializing Phase B modules...")
bias_engine = BiasEngineFvgIfvg()
htf_engine = HTFBiasEngine()

# Hardcoded filters for Stage 1
use_flags = {'daily': False, 'h4': False, 'h1': False, 'm15': False, 'm5': False}
htf_aligned_only = False
require_engulfing = False
require_sweep_engulfing = False

print(f"Processing bars (warmup: {warmup}, preload from {preload_start_ts_arg})...")

# Collect triangle events for batch insert
triangle_events = []
bias_prev = "Neutral"
prev_bar = None
processed_count = 0
bad_skipped = 0
skipped_bars = []
prev_good_close = None
start_index = min(warmup, max(0, len(bars) - 1))

for i, bar_tuple in enumerate(bars):
    bar_dict = {
        'ts': bar_tuple[0],
        'open': float(bar_tuple[1]),
        'high': float(bar_tuple[2]),
        'low': float(bar_tuple[3]),
        'close': float(bar_tuple[4])
    }
    
    # Compute bar timestamps based on table semantics
    if ts_is_open_time:
        # Clean table: ts = bar OPEN time
        bar_open_ts = bar_tuple[0]
        bar_close_ts = bar_tuple[0] + BAR_INTERVAL
    else:
        # Legacy table: ts = bar CLOSE time
        bar_close_ts = bar_tuple[0]
        bar_open_ts = bar_tuple[0] - BAR_INTERVAL
    
    # Debug mode - check if this is the target bar
    is_debug_bar = debug_target_ts and bar_open_ts == debug_target_ts
    
    if is_debug_bar:
        print("\n" + "=" * 80)
        print(f"DEBUG: Target bar found at index {i}")
        print("=" * 80)
        print(f"ts_open:  {bar_open_ts}")
        print(f"ts_close: {bar_close_ts}")
        print(f"OHLC: O={bar_dict['open']:.2f} H={bar_dict['high']:.2f} L={bar_dict['low']:.2f} C={bar_dict['close']:.2f}")
        print(f"bias_prev: {bias_prev}")
    
    # Data hygiene gate
    o, h, l, c = bar_dict['open'], bar_dict['high'], bar_dict['low'], bar_dict['close']
    is_bad = False
    reasons = []
    
    # For clean table: minimal hygiene (should never trigger)
    # For legacy table: full hygiene including corruption heuristics
    if ts_is_open_time:
        # Clean table - only basic integrity checks
        if h < max(o, c) or l > min(o, c) or h < l:
            is_bad = True
            reasons.append('OHLC_INTEGRITY')
        if o < 1000 or h < 1000 or l < 1000 or c < 1000:
            is_bad = True
            reasons.append('PRICE_LT_1000')
    else:
        # Legacy table - full hygiene including corruption heuristics
        if h < max(o, c) or l > min(o, c) or h < l:
            is_bad = True
            reasons.append('OHLC_INTEGRITY')
        if o < 1000 or h < 1000 or l < 1000 or c < 1000:
            is_bad = True
            reasons.append('PRICE_LT_1000')
        if prev_good_close is not None and abs(c - prev_good_close) > 500:
            is_bad = True
            reasons.append('DISCONTINUITY_500')
        if prev_good_close is not None:
            if (h - l) <= 10.0 and abs(c - prev_good_close) >= 150.0:
                is_bad = True
                reasons.append('SMALL_RANGE_BIG_GAP_150')
        if prev_good_close is not None and (o == h == l == c) and abs(c - prev_good_close) > 50:
            is_bad = True
            reasons.append('FLAT_DISCONTINUITY_50')
    
    if is_bad:
        bad_skipped += 1
        bar_close_ts = bar_tuple[0]
        bar_open_ts = bar_close_ts - BAR_INTERVAL
        skipped_bars.append({
            'ts_close': bar_close_ts.isoformat(),
            'ts_open': bar_open_ts.isoformat(),
            'open': o,
            'high': h,
            'low': l,
            'close': c,
            'prev_good_close': prev_good_close,
            'reasons': reasons
        })
        processed_count += 1
        continue
    
    # Module 2: Bias
    bias_1m = bias_engine.update(bar_dict, debug=False)
    
    if is_debug_bar:
        print(f"bias_after: {bias_1m}")
        print(f"\nBiasEngine state after update:")
        ath_str = f"{bias_engine.ath:.2f}" if bias_engine.ath is not None else "None"
        atl_str = f"{bias_engine.atl:.2f}" if bias_engine.atl is not None else "None"
        prev_ath_str = f"{bias_engine.prev_ath:.2f}" if bias_engine.prev_ath is not None else "None"
        prev_atl_str = f"{bias_engine.prev_atl:.2f}" if bias_engine.prev_atl is not None else "None"
        print(f"  ATH: {ath_str}")
        print(f"  ATL: {atl_str}")
        print(f"  prev_ATH: {prev_ath_str}")
        print(f"  prev_ATL: {prev_atl_str}")
        print(f"  bull_fvg arrays: {len(bias_engine.bull_fvg_highs)} items")
        print(f"  bear_fvg arrays: {len(bias_engine.bear_fvg_highs)} items")
        print(f"  bull_ifvg arrays: {len(bias_engine.bull_ifvg_highs)} items")
        print(f"  bear_ifvg arrays: {len(bias_engine.bear_ifvg_highs)} items")
        
        # Show which condition triggered bias change
        if bias_1m != bias_prev:
            print(f"\n*** BIAS CHANGED: {bias_prev} -> {bias_1m}")
            if bias_engine.prev_ath and bar_dict['close'] > bias_engine.prev_ath:
                print(f"  Trigger: ATH break (close {bar_dict['close']:.2f} > prev_ATH {bias_engine.prev_ath:.2f})")
            elif bias_engine.prev_atl and bar_dict['close'] < bias_engine.prev_atl:
                print(f"  Trigger: ATL break (close {bar_dict['close']:.2f} < prev_ATL {bias_engine.prev_atl:.2f})")
            else:
                print(f"  Trigger: FVG/IFVG condition")
    
    # Module 3: HTF Biases
    htf_biases = htf_engine.update_ltf_bar(bar_dict)
    
    # Module 4: HTF Alignment
    biases_dict = {
        'daily': htf_biases['daily_bias'],
        'h4': htf_biases['h4_bias'],
        'h1': htf_biases['h1_bias'],
        'm15': htf_biases['m15_bias'],
        'm5': htf_biases['m5_bias']
    }
    htf_bull, htf_bear = compute_htf_alignment(biases_dict, use_flags)
    
    # Module 5: Signal Generation (only after warmup AND within insert range)
    if prev_bar is not None and i >= start_index:
        # Check if this bar's OPEN time is within insert range
        if bar_open_ts >= insert_open_start and bar_open_ts <= insert_open_end:
            prev_bar_obj = Bar(prev_bar['open'], prev_bar['high'], prev_bar['low'], prev_bar['close'])
            curr_bar_obj = Bar(bar_dict['open'], bar_dict['high'], bar_dict['low'], bar_dict['close'])
            engulfing = detect_engulfing(prev_bar_obj, curr_bar_obj)
            
            signals = generate_signals(
                bias=bias_1m,
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
            
            if is_debug_bar:
                print(f"\nSignal generation:")
                print(f"  show_bull_triangle: {signals['show_bull_triangle']}")
                print(f"  show_bear_triangle: {signals['show_bear_triangle']}")
                if signals['show_bull_triangle']:
                    print(f"  -> BULL triangle at {bar_open_ts}")
                elif signals['show_bear_triangle']:
                    print(f"  -> BEAR triangle at {bar_open_ts}")
                else:
                    print(f"  -> No triangle")
                print("=" * 80 + "\n")
            
            # Triangle timestamp = bar OPEN time (matches TradingView)
            if signals['show_bull_triangle']:
                triangle_events.append((
                    symbol, bar_open_ts, 'BULL',
                    bias_1m, htf_biases['m5_bias'], htf_biases['m15_bias'],
                    htf_biases['h1_bias'], htf_biases['h4_bias'], htf_biases['daily_bias'],
                    htf_bull, htf_bear,
                    require_engulfing, require_sweep_engulfing, htf_aligned_only,
                    table_name, logic_version  # Phase D.0: source tracking
                ))
            
            if signals['show_bear_triangle']:
                triangle_events.append((
                    symbol, bar_open_ts, 'BEAR',
                    bias_1m, htf_biases['m5_bias'], htf_biases['m15_bias'],
                    htf_biases['h1_bias'], htf_biases['h4_bias'], htf_biases['daily_bias'],
                    htf_bull, htf_bear,
                    require_engulfing, require_sweep_engulfing, htf_aligned_only,
                    table_name, logic_version  # Phase D.0: source tracking
                ))
    
    # Update for next iteration
    bias_prev = bias_1m
    prev_bar = bar_dict
    prev_good_close = c
    processed_count += 1
    
    # Progress update every 10,000 bars
    if processed_count % 10000 == 0:
        print(f"  Processed: {processed_count} bars, Triangles: {len(triangle_events)}")

print(f"Processed {processed_count} bars")
print(f"Bad bars skipped: {bad_skipped}")

if skipped_bars:
    print("\nFirst 30 skipped bars:")
    hdr = f"{'TS_OPEN':<20} {'TS_CLOSE':<20} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8} {'PrevClose':>10} Reasons"
    print(hdr)
    print("-" * 120)
    for bar in skipped_bars[:30]:
        reasons_str = ','.join(bar['reasons'])
        prev_str = f"{bar['prev_good_close']:.2f}" if bar['prev_good_close'] is not None else 'None'
        print(f"{bar['ts_open']:<20} {bar['ts_close']:<20} {bar['open']:>8.2f} {bar['high']:>8.2f} {bar['low']:>8.2f} {bar['close']:>8.2f} {prev_str:>10} {reasons_str}")
print(f"Generated {len(triangle_events)} triangle events")

# Batch insert with reconnection logic
if triangle_events:
    print("Inserting triangle events in batches...")
    
    batch_size = 500
    total_batches = (len(triangle_events) + batch_size - 1) // batch_size
    inserted_batches = 0
    retries = 0
    
    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(triangle_events))
        batch = triangle_events[batch_start:batch_end]
        
        # Try to insert batch with automatic reconnection
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                # Use execute_values for efficient batch insert
                execute_values(
                    cursor,
                    """
                    INSERT INTO triangle_events_v1 
                    (symbol, ts, direction, bias_1m, bias_m5, bias_m15, bias_h1, bias_h4, bias_d1,
                     htf_bullish, htf_bearish, require_engulfing, require_sweep_engulfing, htf_aligned_only,
                     source_table, logic_version)
                    VALUES %s
                    ON CONFLICT (symbol, ts, direction) DO NOTHING
                    """,
                    batch,
                    page_size=500
                )
                
                # Commit after each batch
                conn.commit()
                inserted_batches += 1
                
                # Print progress every 10 batches or at end
                if (batch_num + 1) % 10 == 0 or (batch_num + 1) == total_batches:
                    print(f"  Batch {batch_num + 1}/{total_batches}: Processed {batch_end}/{len(triangle_events)} events (commits: {inserted_batches}, retries: {retries})")
                
                break  # Success, exit retry loop
                
            except psycopg2.OperationalError as e:
                if attempt < max_retries:
                    # Reconnect and retry
                    print(f"  ⚠️  Database connection lost at batch {batch_num + 1}, reconnecting...")
                    retries += 1
                    try:
                        cursor.close()
                        conn.close()
                    except:
                        pass
                    conn = psycopg2.connect(database_url)
                    cursor = conn.cursor()
                    print(f"  Retrying batch {batch_num + 1}...")
                else:
                    # Max retries exceeded
                    print(f"  ❌ Failed to insert batch {batch_num + 1} after {max_retries} retries")
                    raise
    
    print(f"Inserted: {inserted_batches} batches ({len(triangle_events)} events)")
    print(f"Retries: {retries}")
else:
    print("No triangle events generated")

cursor.close()
conn.close()

print("-" * 80)
print("[OK] Backfill complete")
