#!/usr/bin/env python3
"""
Phase C: Re-ingest Clean 1M OHLCV Data
Re-queries Databento for specified time range and inserts validated data into clean overlay table

Usage:
    python scripts/phase_c_reingest_clean_1m.py SYMBOL START_TS END_TS
    
Example:
    python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z
"""

import os
import sys
import psycopg2
from psycopg2.extras import execute_values
import databento as db
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import time

def to_databento_continuous(symbol: str, roll_rule: str = "v", rank: int = 0) -> str:
    """
    Convert internal symbol format to Databento continuous symbology.
    
    Accepts:
    - 'GLBX.MDP3:NQ' (our internal form) -> 'NQ.v.0' (default)
    - 'NQ.v.0', 'NQ.c.0', 'NQ.n.0' (already-correct continuous forms)
    
    Args:
        symbol: Internal symbol format or continuous format
        roll_rule: Databento roll rule - 'c' (calendar), 'n' (next), 'v' (volume)
        rank: Contract rank (0=front month, 1=second month, etc.)
    
    Returns:
        Databento continuous format: ROOT.ROLL_RULE.RANK (e.g., 'NQ.v.0')
    """
    if ':' in symbol:
        # 'GLBX.MDP3:NQ' -> root='NQ'
        _, root = symbol.split(':', 1)
        return f"{root}.{roll_rule}.{rank}"
    
    # If already looks like ROOT.ROLL.RANK with valid roll rule, return as-is
    parts = symbol.split('.')
    if len(parts) == 3 and parts[1] in ("c", "n", "v") and parts[2].isdigit():
        return symbol
    
    # Otherwise raise a clear error
    raise ValueError(f"Unsupported symbol format for Databento continuous symbology: {symbol}")

if len(sys.argv) < 4:
    print("Usage: python scripts/phase_c_reingest_clean_1m.py SYMBOL START_TS END_TS [ROLL_RULE] [RANK]")
    print("Example: python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z v 0")
    print("\nRoll rules:")
    print("  c = calendar roll (roll on specific dates)")
    print("  n = next roll (roll to next contract)")
    print("  v = volume roll (roll based on volume, default)")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_ts_str = sys.argv[2]
end_ts_str = sys.argv[3]
roll_rule = sys.argv[4] if len(sys.argv) > 4 else None  # None = use registry
rank = int(sys.argv[5]) if len(sys.argv) > 5 else None  # None = use registry

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set in environment")
    sys.exit(1)

# Connect to database to check symbol registry
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check if symbol registry exists
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'symbol_registry'
    )
""")
registry_exists = cursor.fetchone()[0]

# If roll_rule not provided, try to get from registry
if roll_rule is None and registry_exists:
    cursor.execute("""
        SELECT dataset, root, roll_rule, rank, 
               COALESCE(schema_name, schema) as schema_name, 
               stype_in, is_active,
               vendor_dataset, venue, asset_class
        FROM symbol_registry
        WHERE internal_symbol = %s
    """, (symbol,))
    
    reg = cursor.fetchone()
    if reg:
        dataset, root, roll_rule, rank, schema_name, stype_in, is_active, vendor_dataset, venue, asset_class = reg
        if not is_active:
            print(f"WARNING: Symbol {symbol} is marked as inactive in registry")
        print(f"Using symbol registry:")
        print(f"  Dataset: {vendor_dataset or dataset}")
        print(f"  Root: {root}")
        print(f"  Roll rule: {roll_rule}")
        print(f"  Rank: {rank}")
        print(f"  Schema: {schema_name}")
        if venue:
            print(f"  Venue: {venue}")
        if asset_class:
            print(f"  Asset class: {asset_class}")
    else:
        print(f"WARNING: Symbol {symbol} not found in registry, using defaults")
        roll_rule = "v"
        rank = 0
        dataset = "GLBX.MDP3"  # Default dataset
elif roll_rule is None:
    # No registry, use defaults
    roll_rule = "v"
    rank = 0
    dataset = "GLBX.MDP3"  # Default dataset
else:
    # Roll rule provided, use default dataset
    dataset = "GLBX.MDP3"

# Validate roll rule
if roll_rule not in ("c", "n", "v"):
    print(f"ERROR: Invalid roll rule '{roll_rule}'. Must be 'c', 'n', or 'v'")
    cursor.close()
    conn.close()
    sys.exit(1)

cursor.close()
conn.close()

# Parse timestamps
utc_tz = ZoneInfo('UTC')
start_ts = datetime.fromisoformat(start_ts_str.replace('Z', '+00:00'))
end_ts = datetime.fromisoformat(end_ts_str.replace('Z', '+00:00'))

# Convert to Databento continuous symbology
db_symbol = symbol  # Used for database inserts
db_cont_symbol = to_databento_continuous(symbol, roll_rule, rank)  # Used for Databento query

print(f"Phase C: Clean OHLCV Re-Ingestion")
print(f"DB symbol: {db_symbol}")
print(f"Databento continuous: {db_cont_symbol}")
print(f"Roll rule: {roll_rule} ({'calendar' if roll_rule == 'c' else 'next' if roll_rule == 'n' else 'volume'})")
print(f"Rank: {rank} ({'front month' if rank == 0 else f'{rank} months out'})")
print(f"Range: {start_ts} to {end_ts}")
print("-" * 80)

# Get Databento API key
databento_key = os.environ.get('DATABENTO_API_KEY')
if not databento_key:
    print("ERROR: DATABENTO_API_KEY not set in environment")
    sys.exit(1)

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set in environment")
    sys.exit(1)

# Connect to Databento
print("Connecting to Databento...")
client = db.Historical(databento_key)

# Query historical data
print(f"Querying Databento for {db_cont_symbol} from {start_ts.date()} to {end_ts.date()}...")
try:
    # Use dataset from registry or default
    query_dataset = dataset if 'dataset' in locals() else 'GLBX.MDP3'
    
    data = client.timeseries.get_range(
        dataset=query_dataset,
        symbols=[db_cont_symbol],
        schema='ohlcv-1m',
        start=start_ts,
        end=end_ts,
        stype_in='continuous'
    )
    
    # Convert to DataFrame
    df = data.to_df()
    
    if df.empty:
        print("ERROR: No data returned from Databento")
        sys.exit(1)
    
    print(f"Received {len(df)} bars from Databento")
    
except Exception as e:
    print(f"ERROR querying Databento: {e}")
    sys.exit(1)

# Normalize DataFrame
print("Normalizing data...")
df = df.reset_index()

# Extract timestamp (handle different column names)
timestamp_col = None
for col in ['ts_event', 'timestamp', 'ts']:
    if col in df.columns:
        timestamp_col = col
        break

if timestamp_col is None:
    print(f"ERROR: No timestamp column found. Columns: {list(df.columns)}")
    sys.exit(1)

# Convert to datetime if needed
import pandas as pd
if pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
    df['ts'] = pd.to_datetime(df[timestamp_col], utc=True)
else:
    df['ts'] = pd.to_datetime(df[timestamp_col], unit='ns', utc=True)

# Extract OHLCV
df['open'] = df['open'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['close'] = df['close'].astype(float)
df['volume'] = df['volume'].astype(float) if 'volume' in df.columns else 0

# Add symbol (use DB symbol for database inserts)
df['symbol'] = db_symbol

# Sort by timestamp
df = df.sort_values('ts').reset_index(drop=True)

print(f"Time range: {df['ts'].min()} to {df['ts'].max()}")

# Validation at insert time
print("Validating bars...")
valid_bars = []
skipped_invalid = 0

for idx, row in df.iterrows():
    o, h, l, c = row['open'], row['high'], row['low'], row['close']
    
    # Hard reject validation
    is_invalid = False
    
    # Check 1: OHLC integrity
    if h < max(o, c) or l > min(o, c) or h < l:
        is_invalid = True
    
    # Check 2: Price < 1000
    if o < 1000 or h < 1000 or l < 1000 or c < 1000:
        is_invalid = True
    
    # Check 3: NaN/None
    if pd.isna(o) or pd.isna(h) or pd.isna(l) or pd.isna(c):
        is_invalid = True
    
    if is_invalid:
        skipped_invalid += 1
        continue
    
    # Add to valid bars list
    valid_bars.append((
        symbol,
        row['ts'],
        o,
        h,
        l,
        c,
        row['volume']
    ))

print(f"Valid bars: {len(valid_bars)}")
print(f"Skipped (invalid): {skipped_invalid}")

if len(valid_bars) == 0:
    print("ERROR: No valid bars to insert")
    sys.exit(1)

# Connect to database
print("Connecting to database...")
start_time = time.time()
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check if clean table exists
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'market_bars_ohlcv_1m_clean'
    )
""")
table_exists = cursor.fetchone()[0]

if not table_exists:
    print("ERROR: Table market_bars_ohlcv_1m_clean does not exist")
    print("Run: python database/run_phase_c_clean_ohlcv_migration.py")
    cursor.close()
    conn.close()
    sys.exit(1)

# Check if clean_ingest_runs table exists
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'clean_ingest_runs'
    )
""")
log_table_exists = cursor.fetchone()[0]

# Batch insert with reconnection logic
print("Inserting validated bars in batches...")
batch_size = 500
total_batches = (len(valid_bars) + batch_size - 1) // batch_size
batch_commits = 0
retries = 0

for batch_num in range(total_batches):
    batch_start = batch_num * batch_size
    batch_end = min(batch_start + batch_size, len(valid_bars))
    batch = valid_bars[batch_start:batch_end]
    
    # Try to insert batch with automatic reconnection
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            # Use execute_values for efficient batch insert
            execute_values(
                cursor,
                """
                INSERT INTO market_bars_ohlcv_1m_clean (symbol, ts, open, high, low, close, volume)
                VALUES %s
                ON CONFLICT (symbol, ts) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    created_at = NOW()
                """,
                batch,
                page_size=500
            )
            
            # Commit after each batch
            conn.commit()
            batch_commits += 1
            
            # Print progress
            print(f"  Batch {batch_num + 1}/{total_batches}: Processed {batch_end}/{len(valid_bars)} bars (commits: {batch_commits}, retries: {retries})")
            
            break  # Success, exit retry loop
            
        except psycopg2.OperationalError as e:
            if attempt < max_retries:
                # Reconnect and retry
                print(f"  ⚠️  Database connection lost, reconnecting...")
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

print("-" * 80)
print(f"Ingestion complete:")
print(f"  Total bars: {len(df)}")
print(f"  Valid bars: {len(valid_bars)}")
print(f"  Skipped (invalid): {skipped_invalid}")
print(f"  Batch commits: {batch_commits}")
print(f"  Retries: {retries}")

# Calculate duration
duration_seconds = time.time() - start_time
print(f"  Duration: {duration_seconds:.2f} seconds")

# Log to clean_ingest_runs if table exists
if log_table_exists:
    try:
        cursor.execute("""
            INSERT INTO clean_ingest_runs 
            (symbol, start_ts, end_ts, bars_received, bars_inserted, bars_updated, bars_skipped, 
             batch_commits, retries, duration_seconds, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            db_symbol, start_ts, end_ts, len(df), 
            len(valid_bars) - skipped_invalid,  # Approximate inserted (no exact count with batch)
            0,  # Updated count not tracked with batch insert
            skipped_invalid, batch_commits, retries, duration_seconds, 'success'
        ))
        conn.commit()
        print(f"  ✅ Run logged to clean_ingest_runs")
    except Exception as e:
        print(f"  ⚠️  Failed to log run: {e}")

print("-" * 80)

cursor.close()
conn.close()

print("[OK] Clean OHLCV re-ingestion complete")
