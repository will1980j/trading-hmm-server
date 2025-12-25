#!/usr/bin/env python3
"""
Verify Full 15-Year Ingestion

Checks database for complete ingestion and provides detailed statistics.

Usage:
    python verify_full_ingestion.py
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

def verify_ingestion():
    """Verify full ingestion completion"""
    
    print("="*80)
    print("🔍 VERIFYING FULL 15-YEAR INGESTION")
    print("="*80)
    
    # Load environment
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Query 1: Total row count and time range
        print("\n📊 DATASET STATISTICS")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                COUNT(*) AS row_count,
                MIN(ts) AS min_ts,
                MAX(ts) AS max_ts,
                MIN(ts_ms) AS min_ts_ms,
                MAX(ts_ms) AS max_ts_ms
            FROM market_bars_ohlcv_1m
            WHERE symbol = 'CME_MINI:MNQ1!'
        """)
        result = cursor.fetchone()
        
        row_count = result[0]
        min_ts = result[1]
        max_ts = result[2]
        
        print(f"Total Bars: {row_count:,}")
        print(f"Min Timestamp: {min_ts}")
        print(f"Max Timestamp: {max_ts}")
        
        if min_ts and max_ts:
            duration = max_ts - min_ts
            years = duration.days / 365.25
            print(f"Time Span: {duration.days:,} days ({years:.1f} years)")
        
        # Query 2: Data distribution by year
        print("\n📅 DATA DISTRIBUTION BY YEAR")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                EXTRACT(YEAR FROM ts) AS year,
                COUNT(*) AS bar_count,
                MIN(ts) AS first_bar,
                MAX(ts) AS last_bar
            FROM market_bars_ohlcv_1m
            WHERE symbol = 'CME_MINI:MNQ1!'
            GROUP BY EXTRACT(YEAR FROM ts)
            ORDER BY year
        """)
        
        print(f"{'Year':<8} {'Bars':>12} {'First Bar':<28} {'Last Bar':<28}")
        print("-" * 80)
        
        for row in cursor.fetchall():
            year = int(row[0])
            count = row[1]
            first = row[2]
            last = row[3]
            print(f"{year:<8} {count:>12,} {str(first):<28} {str(last):<28}")
        
        # Query 3: Recent ingestion runs
        print("\n📝 RECENT INGESTION RUNS")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                id,
                started_at,
                finished_at,
                row_count,
                inserted_count,
                updated_count,
                status,
                EXTRACT(EPOCH FROM (finished_at - started_at)) AS duration_seconds
            FROM data_ingest_runs
            ORDER BY id DESC
            LIMIT 10
        """)
        
        print(f"{'ID':<6} {'Status':<10} {'Rows':>12} {'Inserted':>12} {'Updated':>12} {'Duration':>10}")
        print("-" * 80)
        
        for row in cursor.fetchall():
            run_id = row[0]
            status = row[6]
            rows = row[3]
            inserted = row[4]
            updated = row[5]
            duration = row[7]
            
            duration_str = f"{int(duration)}s" if duration else "N/A"
            print(f"{run_id:<6} {status:<10} {rows:>12,} {inserted:>12,} {updated:>12,} {duration_str:>10}")
        
        # Query 4: Ingestion summary
        print("\n📈 INGESTION SUMMARY")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_runs,
                SUM(row_count) AS total_rows_processed,
                SUM(inserted_count) AS total_inserted,
                SUM(updated_count) AS total_updated,
                COUNT(*) FILTER (WHERE status = 'success') AS successful_runs,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs
            FROM data_ingest_runs
        """)
        
        result = cursor.fetchone()
        print(f"Total Runs: {result[0]}")
        print(f"Total Rows Processed: {result[1]:,}")
        print(f"Total Inserted: {result[2]:,}")
        print(f"Total Updated: {result[3]:,}")
        print(f"Successful Runs: {result[4]}")
        print(f"Failed Runs: {result[5]}")
        
        # Query 5: Check for duplicates
        print("\n🔍 DUPLICATE CHECK")
        print("-" * 80)
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT symbol, ts, COUNT(*) AS cnt
                FROM market_bars_ohlcv_1m
                GROUP BY symbol, ts
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        dup_count = cursor.fetchone()[0]
        if dup_count == 0:
            print("✅ No duplicates found - idempotency verified!")
        else:
            print(f"❌ Found {dup_count} duplicate timestamps!")
        
        # Validation
        print("\n✅ VALIDATION")
        print("-" * 80)
        
        if row_count >= 1_000_000:
            print(f"✅ Row count >= 1M: {row_count:,}")
        else:
            print(f"⚠️  Row count < 1M: {row_count:,}")
        
        if min_ts and min_ts.year <= 2011:
            print(f"✅ Min timestamp is historical: {min_ts}")
        else:
            print(f"⚠️  Min timestamp not historical enough: {min_ts}")
        
        if max_ts and max_ts.year >= 2025:
            print(f"✅ Max timestamp is recent: {max_ts}")
        else:
            print(f"⚠️  Max timestamp not recent: {max_ts}")
        
        if dup_count == 0:
            print(f"✅ No duplicates (idempotent)")
        else:
            print(f"❌ Has duplicates")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ VERIFICATION COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    verify_ingestion()
