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
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

def run_migration():
    """Execute the Databento OHLCV schema migration"""
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment")
        print("   Set DATABASE_URL in .env file or environment variables")
        sys.exit(1)
    
    # Get absolute path to SQL file (safe from CWD issues)
    script_dir = Path(__file__).resolve().parent
    migration_file = script_dir / 'databento_ohlcv_schema.sql'
    
    print("🚀 Running Databento OHLCV schema migration...")
    print(f"   SQL file: {migration_file}")
    
    # Verify file exists
    if not migration_file.exists():
        print(f"❌ ERROR: Migration file not found: {migration_file}")
        sys.exit(1)
    
    # Read migration SQL
    migration_sql = migration_file.read_text(encoding='utf-8')
    
    # Validate SQL is not empty
    if len(migration_sql.strip()) == 0:
        print(f"❌ ERROR: Schema SQL is empty or contains only whitespace")
        print(f"   File: {migration_file}")
        sys.exit(1)
    
    print(f"   SQL file size: {len(migration_sql):,} bytes")
    
    # Parse SQL into individual statements
    # Remove comment-only lines and split on semicolons
    statements = []
    for line in migration_sql.split('\n'):
        # Skip lines that are only comments
        stripped = line.strip()
        if stripped.startswith('--') or len(stripped) == 0:
            continue
        statements.append(line)
    
    # Rejoin and split on semicolons
    cleaned_sql = '\n'.join(statements)
    statement_chunks = cleaned_sql.split(';')
    
    # Filter out empty statements
    valid_statements = []
    for chunk in statement_chunks:
        chunk = chunk.strip()
        if len(chunk) > 0:
            valid_statements.append(chunk)
    
    if len(valid_statements) == 0:
        print(f"❌ ERROR: No valid SQL statements found in file")
        print(f"   File: {migration_file}")
        sys.exit(1)
    
    print(f"   Statements to execute: {len(valid_statements)}")
    print(f"   Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    # Execute migration with transaction
    conn = None
    cursor = None
    
    try:
        # Connect with autocommit disabled (transaction mode)
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Execute each statement
        for idx, statement in enumerate(valid_statements, 1):
            try:
                if len(statement.strip()) > 0:  # Double-check not empty
                    cursor.execute(statement)
                    print(f"   ✅ Statement {idx}/{len(valid_statements)} executed")
            except Exception as stmt_error:
                print(f"\n❌ ERROR executing statement {idx}/{len(valid_statements)}:")
                print(f"   {stmt_error}")
                print(f"\n   Statement preview:")
                preview = statement[:200] + ('...' if len(statement) > 200 else '')
                print(f"   {preview}")
                conn.rollback()
                raise
        
        # Commit transaction
        conn.commit()
        print(f"\n✅ Transaction committed successfully")
        
        # Verify tables created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('market_bars_ohlcv_1m', 'data_ingest_runs')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n✅ Migration completed successfully!")
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
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            print("   Transaction rolled back")
        sys.exit(1)
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()
