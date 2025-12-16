#!/usr/bin/env python3
"""
Run indicator export schema migration.
Creates tables for triangle-canonical trade identity.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Execute the indicator export schema migration."""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print("🔄 Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("📖 Reading schema file...")
    with open('database/indicator_export_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    try:
        print("🚀 Executing migration...")
        cursor.execute(schema_sql)
        conn.commit()
        
        print("\n✅ Migration complete!")
        
        # Verify tables were created
        print("\n📊 Verifying tables...")
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_name IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("\nTables created:")
            for table_name, col_count in tables:
                print(f"  ✅ {table_name} ({col_count} columns)")
        else:
            print("  ⚠️  No tables found (may already exist)")
        
        # Verify indexes
        print("\n📇 Verifying indexes...")
        cursor.execute("""
            SELECT tablename, COUNT(*) as index_count
            FROM pg_indexes 
            WHERE tablename IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger')
            GROUP BY tablename
            ORDER BY tablename
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            print("\nIndexes created:")
            for table_name, idx_count in indexes:
                print(f"  ✅ {table_name} ({idx_count} indexes)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
