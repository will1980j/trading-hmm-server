#!/usr/bin/env python3
"""
Create execution_tasks table in Railway PostgreSQL database
Only creates the table if it does not exist
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_execution_tasks_table():
    """Create execution_tasks table"""
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        # Connect to database
        print("🔌 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create table with exact schema provided
        print("📋 Creating execution_tasks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_tasks (
                id SERIAL PRIMARY KEY,
                trade_id VARCHAR(64),
                event_type VARCHAR(50),
                payload JSONB,
                attempts INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        conn.commit()
        print("✅ Table created successfully")
        
        # Verify table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'execution_tasks'
            );
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✅ Verified: execution_tasks table exists")
            
            # Get column information
            cursor.execute("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'execution_tasks'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📊 Table Schema:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (default: {col[2]})")
        else:
            print("❌ Table verification failed")
            return False
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_execution_tasks_table()
    exit(0 if success else 1)
