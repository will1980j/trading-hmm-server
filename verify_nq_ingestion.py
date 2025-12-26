#!/usr/bin/env python3
"""Verify NQ 15-year data ingestion"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check NQ data
cursor.execute("""
    SELECT 
        COUNT(*) as total_bars,
        MIN(ts) as earliest_bar,
        MAX(ts) as latest_bar,
        (SELECT close FROM market_bars_ohlcv_1m 
         WHERE symbol = 'GLBX.MDP3:NQ' 
         ORDER BY ts DESC LIMIT 1) as latest_close
    FROM market_bars_ohlcv_1m
    WHERE symbol = 'GLBX.MDP3:NQ'
""")

result = cursor.fetchone()

print("=" * 80)
print("NQ 15-YEAR DATA VERIFICATION")
print("=" * 80)

if result and result[0] > 0:
    print(f"✅ NQ Data Ingested Successfully")
    print(f"\n   Total Bars: {result[0]:,}")
    print(f"   Date Range: {result[1]} to {result[2]}")
    print(f"   Latest Close: ${result[3]:,.2f}")
    
    # Calculate years
    years = (result[2] - result[1]).days / 365.25
    print(f"   Years of Data: {years:.1f}")
    
else:
    print("❌ No NQ data found")

# Check ingestion run
cursor.execute("""
    SELECT id, dataset, row_count, inserted_count, started_at, finished_at, status
    FROM data_ingest_runs
    WHERE dataset = 'nq_ohlcv_1m'
    ORDER BY started_at DESC
    LIMIT 1
""")

run = cursor.fetchone()
if run:
    print(f"\n📊 Latest Ingestion Run:")
    print(f"   Run ID: {run[0]}")
    print(f"   Dataset: {run[1]}")
    print(f"   Rows Processed: {run[2]:,}")
    print(f"   Inserted: {run[3]:,}")
    print(f"   Started: {run[4]}")
    print(f"   Finished: {run[5]}")
    print(f"   Status: {run[6]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ VERIFICATION COMPLETE")
print("=" * 80)
