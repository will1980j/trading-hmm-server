#!/usr/bin/env python3
"""
Debug Homepage Databento Stats

Tests the exact query used in the homepage route to diagnose the issue.

Usage:
    python debug_homepage_databento_stats.py
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def test_databento_stats_query():
    """Test the exact query used in homepage route"""
    
    print("="*80)
    print("🔍 DEBUGGING HOMEPAGE DATABENTO STATS QUERY")
    print("="*80)
    
    # Load environment
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        sys.exit(1)
    
    print(f"\n📊 Testing query against: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    try:
        # Connect
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Connected")
        
        # Execute exact query from homepage route
        print("\n📝 Executing query...")
        cursor.execute("""
            SELECT 
                COUNT(*) as row_count,
                MIN(ts) as min_ts,
                MAX(ts) as max_ts,
                (SELECT close FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'CME_MINI:MNQ1!' 
                 ORDER BY ts DESC LIMIT 1) as latest_close,
                (SELECT ts FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'CME_MINI:MNQ1!' 
                 ORDER BY ts DESC LIMIT 1) as latest_ts
            FROM market_bars_ohlcv_1m
            WHERE symbol = 'CME_MINI:MNQ1!'
        """)
        
        result = cursor.fetchone()
        print("✅ Query executed")
        
        # Display results
        print("\n📊 QUERY RESULTS:")
        print("-" * 80)
        
        if result:
            print(f"Row Count:     {result[0]:,}")
            print(f"Min TS:        {result[1]}")
            print(f"Max TS:        {result[2]}")
            print(f"Latest Close:  {result[3]}")
            print(f"Latest TS:     {result[4]}")
            
            # Check if data exists
            if result[0] > 0:
                print("\n✅ DATA EXISTS")
                
                # Format as homepage would
                databento_stats = {
                    'row_count': result[0],
                    'min_ts': result[1].strftime('%Y-%m-%d') if result[1] else None,
                    'max_ts': result[2].strftime('%Y-%m-%d') if result[2] else None,
                    'latest_close': float(result[3]) if result[3] else None,
                    'latest_ts': result[4].strftime('%Y-%m-%d %H:%M') if result[4] else None
                }
                
                print("\n📦 FORMATTED FOR HOMEPAGE:")
                print("-" * 80)
                for key, value in databento_stats.items():
                    print(f"{key:15} = {value}")
                
                print("\n✅ Stats would display correctly on homepage")
            else:
                print("\n❌ NO DATA - row_count is 0")
        else:
            print("❌ Query returned None")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ DATABASE CONNECTION ERROR:")
        print(f"   {e}")
        print("\n💡 Possible causes:")
        print("   - DATABASE_URL is incorrect")
        print("   - Database is not accessible")
        print("   - Network/firewall issues")
        
    except psycopg2.ProgrammingError as e:
        print(f"\n❌ SQL ERROR:")
        print(f"   {e}")
        print("\n💡 Possible causes:")
        print("   - Table 'market_bars_ohlcv_1m' doesn't exist")
        print("   - Run migration: python database/run_databento_migration.py")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

def check_table_exists():
    """Check if the table exists"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING TABLE EXISTENCE")
    print("="*80)
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'market_bars_ohlcv_1m'
            )
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✅ Table 'market_bars_ohlcv_1m' exists")
            
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m")
            count = cursor.fetchone()[0]
            print(f"✅ Table has {count:,} rows")
            
            # Check for CME_MINI:MNQ1! specifically
            cursor.execute("""
                SELECT COUNT(*) FROM market_bars_ohlcv_1m 
                WHERE symbol = 'CME_MINI:MNQ1!'
            """)
            mnq_count = cursor.fetchone()[0]
            print(f"✅ CME_MINI:MNQ1! has {mnq_count:,} rows")
            
        else:
            print("❌ Table 'market_bars_ohlcv_1m' does NOT exist")
            print("\n💡 Run migration:")
            print("   python database/run_databento_migration.py")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking table: {e}")

if __name__ == '__main__':
    check_table_exists()
    test_databento_stats_query()
    
    print("\n" + "="*80)
    print("🔍 DIAGNOSIS COMPLETE")
    print("="*80)
    print("\nIf query works here but not on homepage:")
    print("1. Check Railway logs for errors")
    print("2. Verify DATABASE_URL is same on Railway")
    print("3. Check if table exists on Railway database")
    print("4. Restart Railway deployment")
    print("="*80)
