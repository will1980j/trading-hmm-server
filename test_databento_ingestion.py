#!/usr/bin/env python3
"""
Test Databento Ingestion System

Quick verification that all components are working correctly.

Usage:
    python test_databento_ingestion.py
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def test_database_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("   ❌ DATABASE_URL not found in environment")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   ✅ Connected to PostgreSQL")
        print(f"   Version: {version.split(',')[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def test_tables_exist():
    """Test that required tables exist"""
    print("\n📋 Testing table existence...")
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check for tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('market_bars_ohlcv_1m', 'data_ingest_runs')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        expected_tables = ['data_ingest_runs', 'market_bars_ohlcv_1m']
        found_tables = [t[0] for t in tables]
        
        for table in expected_tables:
            if table in found_tables:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing")
                print(f"      Run: python database/run_databento_migration.py")
        
        cursor.close()
        conn.close()
        
        return len(found_tables) == len(expected_tables)
        
    except Exception as e:
        print(f"   ❌ Table check failed: {e}")
        return False

def test_table_structure():
    """Test table structure"""
    print("\n🏗️  Testing table structure...")
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check market_bars_ohlcv_1m columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'market_bars_ohlcv_1m'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        required_columns = [
            'vendor', 'schema', 'symbol', 'ts', 'ts_ms',
            'open', 'high', 'low', 'close', 'volume',
            'ingestion_run_id', 'created_at'
        ]
        
        found_columns = [c[0] for c in columns]
        
        print("   market_bars_ohlcv_1m columns:")
        for col in required_columns:
            if col in found_columns:
                print(f"      ✅ {col}")
            else:
                print(f"      ❌ {col} missing")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'market_bars_ohlcv_1m'
        """)
        indexes = cursor.fetchall()
        
        print(f"\n   Indexes: {len(indexes)} found")
        for idx in indexes:
            print(f"      - {idx[0]}")
        
        cursor.close()
        conn.close()
        
        return all(col in found_columns for col in required_columns)
        
    except Exception as e:
        print(f"   ❌ Structure check failed: {e}")
        return False

def test_data_stats():
    """Test current data statistics"""
    print("\n📊 Testing data statistics...")
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Bar count
        cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m")
        bar_count = cursor.fetchone()[0]
        print(f"   Bars in database: {bar_count:,}")
        
        if bar_count > 0:
            # Time range
            cursor.execute("""
                SELECT MIN(ts), MAX(ts) 
                FROM market_bars_ohlcv_1m
            """)
            min_ts, max_ts = cursor.fetchone()
            print(f"   Time range: {min_ts} to {max_ts}")
            
            # Latest bar
            cursor.execute("""
                SELECT symbol, ts, close 
                FROM market_bars_ohlcv_1m 
                ORDER BY ts DESC LIMIT 1
            """)
            symbol, ts, close = cursor.fetchone()
            print(f"   Latest bar: {symbol} @ {ts} = {close}")
        
        # Ingestion runs
        cursor.execute("SELECT COUNT(*) FROM data_ingest_runs")
        run_count = cursor.fetchone()[0]
        print(f"   Ingestion runs: {run_count}")
        
        if run_count > 0:
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM data_ingest_runs 
                GROUP BY status
            """)
            statuses = cursor.fetchall()
            for status, count in statuses:
                print(f"      {status}: {count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Stats check failed: {e}")
        return False

def test_ingestion_script():
    """Test that ingestion script exists and is executable"""
    print("\n📝 Testing ingestion script...")
    
    script_path = 'scripts/ingest_databento_ohlcv_1m.py'
    
    if os.path.exists(script_path):
        print(f"   ✅ Script exists: {script_path}")
        
        # Check if executable
        if os.access(script_path, os.X_OK):
            print(f"   ✅ Script is executable")
        else:
            print(f"   ⚠️  Script not executable (run: chmod +x {script_path})")
        
        # Check imports
        try:
            with open(script_path, 'r') as f:
                content = f.read()
                required_imports = ['databento', 'zstandard', 'pandas', 'psycopg2']
                for imp in required_imports:
                    if imp in content:
                        print(f"   ✅ Imports {imp}")
                    else:
                        print(f"   ❌ Missing import: {imp}")
        except Exception as e:
            print(f"   ❌ Failed to read script: {e}")
        
        return True
    else:
        print(f"   ❌ Script not found: {script_path}")
        return False

def test_documentation():
    """Test that documentation exists"""
    print("\n📚 Testing documentation...")
    
    readme_path = 'data/databento/mnq/ohlcv_1m/README.md'
    
    if os.path.exists(readme_path):
        print(f"   ✅ README exists: {readme_path}")
        
        with open(readme_path, 'r') as f:
            content = f.read()
            sections = [
                'Directory Structure',
                'Data Format',
                'Ingestion',
                'Verification',
                'Troubleshooting'
            ]
            for section in sections:
                if section in content:
                    print(f"   ✅ Section: {section}")
                else:
                    print(f"   ❌ Missing section: {section}")
        
        return True
    else:
        print(f"   ❌ README not found: {readme_path}")
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("🧪 DATABENTO INGESTION SYSTEM TEST")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Tables Exist", test_tables_exist()))
    results.append(("Table Structure", test_table_structure()))
    results.append(("Data Statistics", test_data_stats()))
    results.append(("Ingestion Script", test_ingestion_script()))
    results.append(("Documentation", test_documentation()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - System ready for use!")
        print("\nNext steps:")
        print("1. Run migration: python database/run_databento_migration.py")
        print("2. Ingest data: python scripts/ingest_databento_ohlcv_1m.py --input <file>")
        print("3. Verify API: curl http://localhost:5000/api/market-data/mnq/ohlcv-1m/stats")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        sys.exit(1)
    
    print("="*80)

if __name__ == '__main__':
    main()
