#!/usr/bin/env python3
"""
Verify Databento Migration Runner

Quick test to ensure the migration runner works correctly.

Usage:
    python verify_databento_migration.py
"""

import os
import sys
from pathlib import Path

def verify_sql_file():
    """Verify SQL file exists and is non-empty"""
    print("📄 Verifying SQL file...")
    
    sql_file = Path('database/databento_ohlcv_schema.sql')
    
    if not sql_file.exists():
        print(f"   ❌ SQL file not found: {sql_file}")
        return False
    
    content = sql_file.read_text(encoding='utf-8')
    
    if len(content.strip()) == 0:
        print(f"   ❌ SQL file is empty")
        return False
    
    # Count statements (rough estimate)
    statements = [s.strip() for s in content.split(';') if s.strip()]
    
    print(f"   ✅ SQL file exists: {sql_file}")
    print(f"   ✅ File size: {len(content):,} bytes")
    print(f"   ✅ Estimated statements: {len(statements)}")
    
    # Check for expected tables
    if 'market_bars_ohlcv_1m' in content:
        print(f"   ✅ Contains market_bars_ohlcv_1m table")
    else:
        print(f"   ❌ Missing market_bars_ohlcv_1m table")
        return False
    
    if 'data_ingest_runs' in content:
        print(f"   ✅ Contains data_ingest_runs table")
    else:
        print(f"   ❌ Missing data_ingest_runs table")
        return False
    
    return True

def verify_migration_script():
    """Verify migration script exists and has correct imports"""
    print("\n📝 Verifying migration script...")
    
    script_file = Path('database/run_databento_migration.py')
    
    if not script_file.exists():
        print(f"   ❌ Migration script not found: {script_file}")
        return False
    
    content = script_file.read_text(encoding='utf-8')
    
    print(f"   ✅ Migration script exists: {script_file}")
    
    # Check for required imports
    required_imports = [
        'from pathlib import Path',
        'import psycopg2',
        'from dotenv import load_dotenv'
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"   ✅ Has import: {imp}")
        else:
            print(f"   ❌ Missing import: {imp}")
            return False
    
    # Check for key features
    features = [
        ('Path(__file__).resolve().parent', 'Absolute path resolution'),
        ('migration_file.exists()', 'File existence check'),
        ('len(migration_sql.strip()) == 0', 'Empty SQL check'),
        ('conn.autocommit = False', 'Transaction mode'),
        ('conn.rollback()', 'Rollback on error'),
        ('conn.commit()', 'Commit on success')
    ]
    
    for code, description in features:
        if code in content:
            print(f"   ✅ Has feature: {description}")
        else:
            print(f"   ❌ Missing feature: {description}")
            return False
    
    return True

def verify_environment():
    """Verify environment is set up"""
    print("\n🔧 Verifying environment...")
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print(f"   ✅ .env file exists")
    else:
        print(f"   ⚠️  .env file not found (may use environment variables)")
    
    # Check for DATABASE_URL
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Mask password in output
        if '@' in database_url:
            parts = database_url.split('@')
            masked = parts[0].split(':')[0] + ':****@' + parts[1]
        else:
            masked = 'postgresql://****'
        print(f"   ✅ DATABASE_URL is set: {masked}")
    else:
        print(f"   ❌ DATABASE_URL not found in environment")
        print(f"      Set DATABASE_URL in .env or environment variables")
        return False
    
    return True

def main():
    """Run all verifications"""
    print("="*80)
    print("🧪 DATABENTO MIGRATION VERIFICATION")
    print("="*80)
    
    results = []
    
    # Run verifications
    results.append(("SQL File", verify_sql_file()))
    results.append(("Migration Script", verify_migration_script()))
    results.append(("Environment", verify_environment()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ ALL CHECKS PASSED - Ready to run migration!")
        print("\nNext step:")
        print("   python database/run_databento_migration.py")
    else:
        print("\n❌ SOME CHECKS FAILED - Review errors above")
        sys.exit(1)
    
    print("="*80)

if __name__ == '__main__':
    main()
