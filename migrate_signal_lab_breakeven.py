#!/usr/bin/env python3
"""
Signal Lab Breakeven Migration Script
Adds new breakeven tracking columns to signal_lab_trades table
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_url():
    """Get database URL from environment or Railway"""
    return os.getenv('DATABASE_URL') or os.getenv('RAILWAY_DATABASE_URL')

def migrate_signal_lab_breakeven():
    """Add new breakeven columns to signal_lab_trades table"""
    
    database_url = get_database_url()
    if not database_url:
        print("ERROR: No DATABASE_URL found in environment")
        return False
    
    try:
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        print("Starting Signal Lab breakeven migration...")
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'signal_lab_trades'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("ERROR: signal_lab_trades table not found")
            return False
        
        # Add new columns
        migration_sql = """
        ALTER TABLE signal_lab_trades 
        ADD COLUMN IF NOT EXISTS mfe_none DECIMAL(10,2) DEFAULT 0,
        ADD COLUMN IF NOT EXISTS be1_level DECIMAL(10,2) DEFAULT 1,
        ADD COLUMN IF NOT EXISTS be1_hit BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS mfe1 DECIMAL(10,2) DEFAULT 0,
        ADD COLUMN IF NOT EXISTS be2_level DECIMAL(10,2) DEFAULT 2,
        ADD COLUMN IF NOT EXISTS be2_hit BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS mfe2 DECIMAL(10,2) DEFAULT 0;
        """
        
        cursor.execute(migration_sql)
        
        # Migrate existing data (move old mfe to mfe_none)
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET mfe_none = COALESCE(mfe, 0)
            WHERE mfe_none = 0 AND mfe IS NOT NULL;
        """)
        
        rows_updated = cursor.rowcount
        
        conn.commit()
        
        print(f"SUCCESS: Migration completed successfully!")
        print(f"Updated {rows_updated} existing records")
        print("Added columns: mfe_none, be1_level, be1_hit, mfe1, be2_level, be2_hit, mfe2")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_signal_lab_breakeven()
    sys.exit(0 if success else 1)