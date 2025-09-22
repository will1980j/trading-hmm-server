#!/usr/bin/env python3
"""Run database migration to add target_r_score column with Railway URL"""

import psycopg2
from psycopg2.extras import RealDictCursor

def run_migration():
    try:
        # Railway PostgreSQL URL - replace with your actual URL
        database_url = "postgresql://postgres:LlBYKJHGdOJGJKJGJKJGJKJGJKJGJKJG@junction.proxy.rlwy.net:47292/railway"
        
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