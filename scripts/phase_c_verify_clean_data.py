#!/usr/bin/env python3
"""
Phase C: Verify Clean OHLCV Data
Checks if clean table has correct data at critical timestamps

Usage:
    python scripts/phase_c_verify_clean_data.py
"""

import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

# Critical timestamps to verify (TV time → UTC)
CRITICAL_TIMESTAMPS = [
    {
        'tv_time': '19:14',
        'utc': datetime(2025, 12, 2, 0, 14, 0, tzinfo=ZoneInfo('UTC')),
        'expected': {'open': 25406.25, 'high': 25408.75, 'low': 25400.25, 'close': 25402.50}
    },
    {
        'tv_time': '19:15',
        'utc': datetime(2025, 12, 2, 0, 15, 0, tzinfo=ZoneInfo('UTC')),
        'expected': {'open': 25403.75, 'high': 25409.75, 'low': 25403.75, 'close': 25406.75}
    }
]

SYMBOL = 'GLBX.MDP3:NQ'

print("Phase C: Clean OHLCV Data Verification")
print("=" * 80)

# Connect to database
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    exit(1)

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
    print("❌ Clean table does not exist")
    print("   Run: python database/run_phase_c_clean_ohlcv_migration.py")
    cursor.close()
    conn.close()
    exit(1)

print("✅ Clean table exists")

# Check row count
cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m_clean WHERE symbol = %s", (SYMBOL,))
row_count = cursor.fetchone()[0]
print(f"   Rows in clean table: {row_count}")

if row_count == 0:
    print("\n❌ Clean table is empty")
    print("   Run: python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z")
    cursor.close()
    conn.close()
    exit(1)

print("\n" + "=" * 80)
print("Verifying Critical Timestamps")
print("=" * 80)

all_match = True

for check in CRITICAL_TIMESTAMPS:
    tv_time = check['tv_time']
    utc = check['utc']
    expected = check['expected']
    
    cursor.execute("""
        SELECT open, high, low, close
        FROM market_bars_ohlcv_1m_clean
        WHERE symbol = %s AND ts = %s
    """, (SYMBOL, utc))
    
    row = cursor.fetchone()
    
    print(f"\nTV {tv_time} (UTC {utc}):")
    
    if not row:
        print("  ❌ NO DATA FOUND")
        all_match = False
        continue
    
    actual = {
        'open': float(row[0]),
        'high': float(row[1]),
        'low': float(row[2]),
        'close': float(row[3])
    }
    
    print(f"  Actual:   O={actual['open']:>8.2f} H={actual['high']:>8.2f} L={actual['low']:>8.2f} C={actual['close']:>8.2f}")
    print(f"  Expected: O={expected['open']:>8.2f} H={expected['high']:>8.2f} L={expected['low']:>8.2f} C={expected['close']:>8.2f}")
    
    # Check if values match (within 0.01 tolerance)
    matches = all(
        abs(actual[key] - expected[key]) < 0.01
        for key in ['open', 'high', 'low', 'close']
    )
    
    if matches:
        print("  ✅ MATCH")
    else:
        print("  ❌ MISMATCH")
        all_match = False

print("\n" + "=" * 80)

if all_match:
    print("✅ ALL CRITICAL TIMESTAMPS VERIFIED")
    print("   Clean data matches TradingView!")
    print("\nNext step:")
    print("   Run backfill: $env:PURGE=\"1\"; python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z")
else:
    print("❌ VERIFICATION FAILED")
    print("   Clean data does NOT match TradingView")
    print("\nNext step:")
    print("   Re-ingest clean data: python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z")
    print("   (Requires DATABENTO_API_KEY in .env)")

print("=" * 80)

cursor.close()
conn.close()

exit(0 if all_match else 1)
