#!/usr/bin/env python3
"""
Run Databento OHLCV Schema Migration

Executes the databento_ohlcv_schema.sql migration to create tables and indexes.
Safe to run multiple times (uses IF NOT EXISTS).

Usage:
    python database/run_databento_migration.py
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    """Execute the Databento OHLCV schema migration"""
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment")
        print("   Set DATABASE_URL in .env file or environment variables")
        sys.exit(1)
    
    # Read migration SQL
    migration_file = os.path.join(
        os.path.dirname(__file__),
        'databento_ohlcv_schema.sql'
    )
    
    if not os.path.exists(migration_file):
        print(f"❌ ERROR: Migration file not found: {migration_file}")
        sys.exit(1)
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    # Execute migration
    print("🚀 Running Databento OHLCV schema migration...")
    print(f"   Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        # Verify tables created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('market_bars_ohlcv_1m', 'data_ingest_runs')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print("\n✅ Migration completed successfully!")
        print(f"   Tables created: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Show table stats
        cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m")
        bar_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM data_ingest_runs")
        run_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current Data:")
        print(f"   market_bars_ohlcv_1m: {bar_count:,} rows")
        print(f"   data_ingest_runs: {run_count:,} rows")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
