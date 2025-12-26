#!/usr/bin/env python3
import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT symbol FROM market_bars_ohlcv_1m WHERE dataset_version_id IS NULL")
symbols = [row[0] for row in cursor.fetchall()]

if not symbols:
    print("✅ No bars need backfill")
    cursor.close()
    conn.close()
    exit(0)

for symbol in symbols:
    cursor.execute("""
        SELECT dataset_version_id, dataset FROM data_ingest_runs
        WHERE dataset_version_id IS NOT NULL
        ORDER BY finished_at DESC LIMIT 1
    """)
    
    version_row = cursor.fetchone()
    if not version_row:
        print(f"❌ {symbol}: No dataset version found")
        continue
    
    version_id = version_row[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT dataset_version_id) FROM data_ingest_runs
        WHERE dataset_version_id IS NOT NULL
    """)
    
    version_count = cursor.fetchone()[0]
    
    if version_count > 1:
        print(f"❌ {symbol}: Multiple versions ({version_count}) - cannot safely backfill")
        print("   Manual intervention required")
        cursor.close()
        conn.close()
        exit(1)
    
    cursor.execute("""
        UPDATE market_bars_ohlcv_1m SET dataset_version_id = %s
        WHERE symbol = %s AND dataset_version_id IS NULL
    """, (version_id, symbol))
    
    updated = cursor.rowcount
    conn.commit()
    print(f"✅ {symbol}: Updated {updated:,} bars to version {version_id}")

cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m WHERE dataset_version_id IS NULL")
unversioned = cursor.fetchone()[0]

cursor.close()
conn.close()

if unversioned > 0:
    print(f"\n❌ {unversioned:,} bars remain unversioned - Phase A gate will FAIL")
    exit(1)

print(f"\n✅ All bars versioned")
