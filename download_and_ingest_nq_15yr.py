#!/usr/bin/env python3
"""
Download and ingest 15 years of NQ 1-minute OHLCV data from Databento

This script:
1. Downloads NQ data from Databento (2010-2025)
2. Ingests into PostgreSQL using existing pipeline
3. Verifies ingestion success
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
SYMBOL = "CME:NQ1!"
DATASET = "nq_ohlcv_1m"
START_DATE = "2010-01-01"
END_DATE = "2025-12-26"
OUTPUT_DIR = Path("data/databento/nq/ohlcv_1m/raw")
OUTPUT_FILE = OUTPUT_DIR / "nq_ohlcv_1m_2010_2025.dbn.zst"

def main():
    print("=" * 80)
    print("DATABENTO NQ 15-YEAR HISTORICAL DATA INGESTION")
    print("=" * 80)
    print(f"Symbol: {SYMBOL}")
    print(f"Date Range: {START_DATE} to {END_DATE}")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 80)
    
    # Step 1: Create directory structure
    print("\n📁 Creating directory structure...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory created: {OUTPUT_DIR}")
    
    # Step 2: Download data from Databento
    print("\n📥 Downloading NQ data from Databento...")
    print("⚠️  This will take 30-60 minutes depending on your internet speed")
    print("⚠️  File size: ~500 MB compressed")
    print()
    
    if OUTPUT_FILE.exists():
        print(f"⚠️  File already exists: {OUTPUT_FILE}")
        response = input("Do you want to re-download? (y/N): ")
        if response.lower() != 'y':
            print("Skipping download, using existing file")
        else:
            print("Re-downloading...")
            download_data()
    else:
        download_data()
    
    # Step 3: Verify file exists
    if not OUTPUT_FILE.exists():
        print(f"\n❌ ERROR: File not found: {OUTPUT_FILE}")
        print("Download may have failed. Check Databento CLI output above.")
        sys.exit(1)
    
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\n✅ File downloaded: {OUTPUT_FILE}")
    print(f"   Size: {file_size_mb:.2f} MB")
    
    # Step 4: Run dry-run validation
    print("\n🧪 Running dry-run validation...")
    dry_run_cmd = [
        "python", "scripts/ingest_databento_ohlcv_1m.py",
        "--input", str(OUTPUT_FILE),
        "--symbol", SYMBOL,
        "--dataset", DATASET,
        "--dry-run",
        "--verbose"
    ]
    
    result = subprocess.run(dry_run_cmd, capture_output=False)
    if result.returncode != 0:
        print("\n❌ Dry-run validation failed!")
        print("Fix errors above before proceeding to production ingestion.")
        sys.exit(1)
    
    # Step 5: Confirm production ingestion
    print("\n" + "=" * 80)
    print("⚠️  READY FOR PRODUCTION INGESTION")
    print("=" * 80)
    print("This will write ~3.9 million bars to your PostgreSQL database.")
    print("Estimated time: 10-30 minutes")
    print("Estimated storage: ~500 MB")
    print()
    response = input("Proceed with production ingestion? (y/N): ")
    
    if response.lower() != 'y':
        print("\n❌ Ingestion cancelled by user")
        sys.exit(0)
    
    # Step 6: Production ingestion
    print("\n💾 Starting production ingestion...")
    ingest_cmd = [
        "python", "scripts/ingest_databento_ohlcv_1m.py",
        "--input", str(OUTPUT_FILE),
        "--symbol", SYMBOL,
        "--dataset", DATASET,
        "--verbose"
    ]
    
    result = subprocess.run(ingest_cmd, capture_output=False)
    if result.returncode != 0:
        print("\n❌ Production ingestion failed!")
        sys.exit(1)
    
    # Step 7: Verify ingestion
    print("\n✅ Verifying ingestion...")
    verify_ingestion()
    
    print("\n" + "=" * 80)
    print("✅ NQ 15-YEAR INGESTION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Create API endpoint: GET /api/market-data/nq/ohlcv-1m/stats")
    print("2. Update homepage with NQ stats")
    print("3. Deploy to Railway")
    print("4. Test production API endpoint")


def download_data():
    """Download NQ data from Databento using CLI"""
    download_cmd = [
        "databento", "download",
        "--dataset", "GLBX.MDP3",
        "--symbols", "NQ.c.0",
        "--schema", "ohlcv-1m",
        "--start", START_DATE,
        "--end", END_DATE,
        "--output", str(OUTPUT_FILE)
    ]
    
    print(f"Running: {' '.join(download_cmd)}")
    result = subprocess.run(download_cmd, capture_output=False)
    
    if result.returncode != 0:
        print("\n❌ Download failed!")
        print("\nTroubleshooting:")
        print("1. Ensure Databento CLI is installed: pip install databento-cli")
        print("2. Authenticate: databento auth login")
        print("3. Check your API key has sufficient credits")
        print("4. Verify symbol and dataset are correct")
        sys.exit(1)


def verify_ingestion():
    """Verify ingestion via database query"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("⚠️  DATABASE_URL not set - skipping verification")
            return
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bars,
                MIN(ts) as earliest_bar,
                MAX(ts) as latest_bar
            FROM market_bars_ohlcv_1m
            WHERE symbol = %s
        """, (SYMBOL,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] > 0:
            print(f"\n✅ Verification successful:")
            print(f"   Total bars: {result[0]:,}")
            print(f"   Date range: {result[1]} to {result[2]}")
        else:
            print(f"\n⚠️  No data found for symbol: {SYMBOL}")
            
    except Exception as e:
        print(f"\n⚠️  Verification failed: {e}")
        print("   (This is non-fatal - check manually)")


if __name__ == "__main__":
    main()
