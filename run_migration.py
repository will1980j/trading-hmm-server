#!/usr/bin/env python3
"""Run database migration to add target_r_score column"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def run_migration():
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ No DATABASE_URL found in environment")
            return False
        
        # Connect to database
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'signal_lab_trades' 
            AND column_name = 'target_r_score'
        """)
        
        if cursor.fetchone():
            print("✅ Column target_r_score already exists")
            return True
        
        # Add the column
        cursor.execute("ALTER TABLE signal_lab_trades ADD COLUMN target_r_score DECIMAL(5,2);")
        conn.commit()
        
        print("✅ Successfully added target_r_score column to signal_lab_trades table")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()