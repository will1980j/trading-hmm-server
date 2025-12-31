#!/usr/bin/env python3
"""
Phase E: Backfill HTF Bias Series
Generate HTF bias timeline from clean 1m OHLCV with forward-fill semantics
"""

import os, sys, psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import subprocess

sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

if len(sys.argv) < 4:
    print("Usage: python scripts/phase_e_backfill_bias_series.py SYMBOL START_DATE END_DATE [WARMUP]")
    print("Example: python scripts/phase_e_backfill_bias_series.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
warmup = int(sys.argv[4]) if len(sys.argv) > 4 else 5

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

# Get logic version
try:
    logic_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                           stderr=subprocess.DEVNULL).decode().strip()
except:
    logic_version = os.environ.get('LOGIC_VERSION', 'unknown')

print(f"Phase E: HTF Bias Series Backfill")
print(f"Symbol: {symbol}")
print(f"Range: {start_date} to {end_date}")
print(f"Warmup: {warmup} bars")
print(f"Logic version: {logic_version}")
print("-" * 80)

# Connect to database
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Verify clean table exists
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'market_bars_ohlcv_1m_clean'
    )
""")
if not cursor.fetchone()[0]:
    print("ERROR: market_bars_ohlcv_1m_clean table does not exist")
    cursor.close()
    conn.close()
    sys.exit(1)

# Fetch 1m bars
print(f"Fetching 1m bars from market_bars_ohlcv_1m_clean...")
cursor.execute("""
    SELECT ts, open, high, low, close 
    FROM market_bars_ohlcv_1m_clean
    WHERE symbol = %s AND ts >= %s AND ts <= %s
    ORDER BY ts ASC
""", (symbol, start_ts, end_ts))

bars_1m = cursor.fetchall()
print(f"Fetched {len(bars_1m)} 1m bars")

if len(bars_1m) < warmup:
    print(f"ERROR: Not enough bars (need >= {warmup})")
    cursor.close()
    conn.close()
    sys.exit(1)

# Initialize bias engines
bias_1m = BiasEngineFvgIfvg()
bias_5m = BiasEngineFvgIfvg()
bias_15m = BiasEngineFvgIfvg()
bias_1h = BiasEngineFvgIfvg()
bias_4h = BiasEngineFvgIfvg()
bias_1d = BiasEngineFvgIfvg()

# HTF aggregators
htf_bars = {
    '5m': {'open': None, 'high': None, 'low': None, 'close': None, 'start_ts': None},
    '15m': {'open': None, 'high': None, 'low': None, 'close': None, 'start_ts': None},
    '1h': {'open': None, 'high': None, 'low': None, 'close': None, 'start_ts': None},
    '4h': {'open': None, 'high': None, 'low': None, 'close': None, 'start_ts': None},
    '1d': {'open': None, 'high': None, 'low': None, 'close': None, 'start_ts': None}
}

# Forward-filled HTF biases
htf_biases_current = {
    '5m': 'Neutral',
    '15m': 'Neutral',
    '1h': 'Neutral',
    '4h': 'Neutral',
    '1d': 'Neutral'
}

def is_htf_bar_close(ts, interval_minutes):
    """Check if this 1m bar closes an HTF bar"""
    minute = ts.minute
    hour = ts.hour
    
    if interval_minutes == 5:
        return minute % 5 == 4  # Closes at :04, :09, :14, etc.
    elif interval_minutes == 15:
        return minute % 15 == 14  # Closes at :14, :29, :44, :59
    elif interval_minutes == 60:
        return minute == 59  # Closes at :59
    elif interval_minutes == 240:
        return minute == 59 and hour % 4 == 3  # Closes at 03:59, 07:59, etc.
    elif interval_minutes == 1440:
        return hour == 23 and minute == 59  # Closes at 23:59
    return False

def get_htf_bar_start(ts, interval_minutes):
    """Get HTF bar start timestamp"""
    minute = ts.minute
    hour = ts.hour
    
    if interval_minutes == 5:
        start_minute = (minute // 5) * 5
        return ts.replace(minute=start_minute, second=0, microsecond=0)
    elif interval_minutes == 15:
        start_minute = (minute // 15) * 15
        return ts.replace(minute=start_minute, second=0, microsecond=0)
    elif interval_minutes == 60:
        return ts.replace(minute=0, second=0, microsecond=0)
    elif interval_minutes == 240:
        start_hour = (hour // 4) * 4
        return ts.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    elif interval_minutes == 1440:
        return ts.replace(hour=0, minute=0, second=0, microsecond=0)
    return ts

print("Processing bars with HTF aggregation...")

bias_series = []
processed_count = 0

for i, bar_tuple in enumerate(bars_1m):
    bar_ts = bar_tuple[0]
    bar_dict = {
        'ts': bar_ts,
        'open': float(bar_tuple[1]),
        'high': float(bar_tuple[2]),
        'low': float(bar_tuple[3]),
        'close': float(bar_tuple[4])
    }
    
    # Update 1m bias
    bias_1m_val = bias_1m.update(bar_dict)
    
    # Update HTF aggregators and biases
    for tf_name, interval_mins in [('5m', 5), ('15m', 15), ('1h', 60), ('4h', 240), ('1d', 1440)]:
        htf_bar = htf_bars[tf_name]
        bar_start = get_htf_bar_start(bar_ts, interval_mins)
        
        # Initialize or update HTF bar
        if htf_bar['start_ts'] is None or htf_bar['start_ts'] != bar_start:
            # New HTF bar starting
            htf_bar['start_ts'] = bar_start
            htf_bar['open'] = bar_dict['open']
            htf_bar['high'] = bar_dict['high']
            htf_bar['low'] = bar_dict['low']
            htf_bar['close'] = bar_dict['close']
        else:
            # Update existing HTF bar
            htf_bar['high'] = max(htf_bar['high'], bar_dict['high'])
            htf_bar['low'] = min(htf_bar['low'], bar_dict['low'])
            htf_bar['close'] = bar_dict['close']
        
        # Check if HTF bar closes
        if is_htf_bar_close(bar_ts, interval_mins):
            # Update HTF bias engine
            htf_bar_dict = {
                'ts': bar_start,
                'open': htf_bar['open'],
                'high': htf_bar['high'],
                'low': htf_bar['low'],
                'close': htf_bar['close']
            }
            
            if tf_name == '5m':
                htf_biases_current['5m'] = bias_5m.update(htf_bar_dict)
            elif tf_name == '15m':
                htf_biases_current['15m'] = bias_15m.update(htf_bar_dict)
            elif tf_name == '1h':
                htf_biases_current['1h'] = bias_1h.update(htf_bar_dict)
            elif tf_name == '4h':
                htf_biases_current['4h'] = bias_4h.update(htf_bar_dict)
            elif tf_name == '1d':
                htf_biases_current['1d'] = bias_1d.update(htf_bar_dict)
    
    # After warmup, store bias series
    if i >= warmup:
        bias_series.append((
            symbol,
            bar_ts,
            bias_1m_val,
            htf_biases_current['5m'],
            htf_biases_current['15m'],
            htf_biases_current['1h'],
            htf_biases_current['4h'],
            htf_biases_current['1d'],
            'market_bars_ohlcv_1m_clean',
            logic_version
        ))
    
    processed_count += 1
    
    # Progress every 50k bars
    if processed_count % 50000 == 0:
        print(f"  Processed: {processed_count} bars, Series: {len(bias_series)}")

print(f"Processed {processed_count} bars")
print(f"Generated {len(bias_series)} bias series entries")

# Batch insert with reconnection
if bias_series:
    print("Inserting bias series in batches...")
    
    batch_size = 500
    total_batches = (len(bias_series) + batch_size - 1) // batch_size
    inserted_batches = 0
    retries = 0
    
    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(bias_series))
        batch = bias_series[batch_start:batch_end]
        
        # Try to insert batch with automatic reconnection
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                execute_values(
                    cursor,
                    """
                    INSERT INTO bias_series_1m_v1 
                    (symbol, ts, bias_1m, bias_5m, bias_15m, bias_1h, bias_4h, bias_1d, 
                     source_table, logic_version)
                    VALUES %s
                    ON CONFLICT (symbol, ts) DO UPDATE SET
                        bias_1m = EXCLUDED.bias_1m,
                        bias_5m = EXCLUDED.bias_5m,
                        bias_15m = EXCLUDED.bias_15m,
                        bias_1h = EXCLUDED.bias_1h,
                        bias_4h = EXCLUDED.bias_4h,
                        bias_1d = EXCLUDED.bias_1d,
                        source_table = EXCLUDED.source_table,
                        logic_version = EXCLUDED.logic_version,
                        created_at = NOW()
                    """,
                    batch,
                    page_size=500
                )
                
                conn.commit()
                inserted_batches += 1
                
                # Progress every 10 batches or at end
                if (batch_num + 1) % 10 == 0 or (batch_num + 1) == total_batches:
                    print(f"  Batch {batch_num + 1}/{total_batches}: Processed {batch_end}/{len(bias_series)} entries (commits: {inserted_batches}, retries: {retries})")
                
                break
                
            except psycopg2.OperationalError as e:
                if attempt < max_retries:
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
                    print(f"  ❌ Failed to insert batch {batch_num + 1} after {max_retries} retries")
                    raise
    
    print(f"Inserted: {inserted_batches} batches ({len(bias_series)} entries)")
    print(f"Retries: {retries}")
else:
    print("No bias series entries generated")

cursor.close()
conn.close()

print("-" * 80)
print("[OK] Bias series backfill complete")
