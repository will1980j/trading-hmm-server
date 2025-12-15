"""
Run Data Quality Schema Migration
Creates tables for reconciliation tracking, conflict management, and quality metrics
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Execute data quality schema migration"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        print("🔄 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📖 Reading schema file...")
        with open('database/data_quality_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        print("🚀 Executing migration...")
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Migration complete!")
        print()
        print("Created tables:")
        print("  - data_quality_reconciliations")
        print("  - data_quality_conflicts")
        print("  - data_quality_metrics")
        print()
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'data_quality%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"Verified {len(tables)} tables created:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
