#!/usr/bin/env python3
"""
Phase C: Copy Validated OHLCV to Clean Table
Copies data from market_bars_ohlcv_1m to market_bars_ohlcv_1m_clean with strict validation

Usage:
    python scripts/phase_c_copy_validated_ohlcv.py SYMBOL START_TS END_TS
    
Example:
    python scripts/phase_c_copy_validated_ohlcv.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z
"""

import os
import sys
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

if len(sys.argv) < 4:
    print("Usage: python scripts/phase_c_copy_validated_ohlcv.py SYMBOL START_TS END_TS")
    print("Example: python scripts/phase_c_copy_validated_ohlcv.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_ts_str = sys.argv[2]
end_ts_str = sys.argv[3]

# Parse timestamps
utc_tz = ZoneInfo('UTC')
start_ts = datetime.fromisoformat(start_ts_str.replace('Z', '+00:00'))
end_ts = datetime.fromisoformat(end_ts_str.replace('Z', '+00:00'))

print(f"Phase C: Copy Validated OHLCV to Clean Table")
print(f"Symbol: {symbol}")
print(f"Range: {start_ts} to {end_ts}")
print("-" * 80)

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set in environment")
    sys.exit(1)

# Connect to database
print("Connecting to database...")
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

# Fetch source data
print(f"Fetching source data from market_bars_ohlcv_1m...")
cursor.execute("""
    SELECT ts, open, high, low, close, volume
    FROM market_bars_ohlcv_1m
    WHERE symbol = %s AND ts >= %s AND ts <= %s
    ORDER BY ts ASC
""", (symbol, start_ts, end_ts))

rows = cursor.fetchall()
print(f"Fetched {len(rows)} bars from source table")

if len(rows) == 0:
    print("ERROR: No data found in source table for specified range")
    cursor.close()
    conn.close()
    sys.exit(1)

# Validate and insert
print("Validating and inserting bars...")
inserted_count = 0
updated_count = 0
skipped_invalid = 0
skipped_details = []

for idx, row in enumerate(rows):
    ts, o, h, l, c, vol = row
    o, h, l, c = float(o), float(h), float(l), float(c)
    
    # Hard reject validation
    is_invalid = False
    reasons = []
    
    # Check 1: OHLC integrity
    if h < max(o, c) or l > min(o, c) or h < l:
        is_invalid = True
        reasons.append('OHLC_INTEGRITY')
    
    # Check 2: Price < 1000
    if o < 1000 or h < 1000 or l < 1000 or c < 1000:
        is_invalid = True
        reasons.append('PRICE_LT_1000')
    
    # Check 3: NaN/None
    if o is None or h is None or l is None or c is None:
        is_invalid = True
        reasons.append('NULL_VALUE')
    
    if is_invalid:
        skipped_invalid += 1
        if len(skipped_details) < 30:
            skipped_details.append({
                'ts': ts,
                'open': o,
                'high': h,
                'low': l,
                'close': c,
                'reasons': reasons
            })
        continue
    
    # Insert with ON CONFLICT DO UPDATE
    cursor.execute("""
        INSERT INTO market_bars_ohlcv_1m_clean (symbol, ts, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, ts) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            created_at = NOW()
        RETURNING (xmax = 0) AS inserted
    """, (symbol, ts, o, h, l, c, vol if vol else 0))
    
    was_inserted = cursor.fetchone()[0]
    if was_inserted:
        inserted_count += 1
    else:
        updated_count += 1
    
    # Progress update every 1000 bars
    if (idx + 1) % 1000 == 0:
        print(f"  Processed: {idx + 1}/{len(rows)} bars")

conn.commit()

print("-" * 80)
print(f"Copy complete:")
print(f"  Total bars: {len(rows)}")
print(f"  Inserted: {inserted_count}")
print(f"  Updated: {updated_count}")
print(f"  Skipped (invalid): {skipped_invalid}")

if skipped_details:
    print(f"\nFirst {len(skipped_details)} skipped bars:")
    print(f"{'TS':<20} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8} Reasons")
    print("-" * 80)
    for bar in skipped_details:
        reasons_str = ','.join(bar['reasons'])
        print(f"{bar['ts']} {bar['open']:>8.2f} {bar['high']:>8.2f} {bar['low']:>8.2f} {bar['close']:>8.2f} {reasons_str}")

print("-" * 80)

cursor.close()
conn.close()

print("[OK] Validated OHLCV copy complete")
