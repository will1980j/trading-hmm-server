"""
Direct table creation via Railway database connection
This bypasses the webhook handler and creates the table directly
"""
import os
import psycopg2
from urllib.parse import urlparse

# Railway database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:vYOEMLXAjHbLtLNqzxWLWGGxjJJVLqYy@autorack.proxy.rlwy.net:47625/railway')

def create_automated_signals_table():
    """Create the automated_signals table directly"""
    
    # Parse database URL
    result = urlparse(DATABASE_URL)
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        cursor = conn.cursor()
        
        # Drop existing table if it exists
        print("Dropping existing table if it exists...")
        cursor.execute("DROP TABLE IF EXISTS automated_signals CASCADE;")
        
        # Create table with all required columns
        print("Creating automated_signals table...")
        create_table_sql = """
        CREATE TABLE automated_signals (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(20) NOT NULL,
            trade_id VARCHAR(100) NOT NULL,
            direction VARCHAR(10),
            entry_price DECIMAL(10, 2),
            stop_loss DECIMAL(10, 2),
            risk_distance DECIMAL(10, 2),
            target_1r DECIMAL(10, 2),
            target_2r DECIMAL(10, 2),
            target_3r DECIMAL(10, 2),
            target_5r DECIMAL(10, 2),
            target_10r DECIMAL(10, 2),
            target_20r DECIMAL(10, 2),
            session VARCHAR(20),
            bias VARCHAR(20),
            current_price DECIMAL(10, 2),
            mfe DECIMAL(10, 4),
            exit_price DECIMAL(10, 2),
            exit_type VARCHAR(20),
            final_mfe DECIMAL(10, 4),
            account_size DECIMAL(15, 2),
            risk_percent DECIMAL(5, 2),
            contracts INTEGER,
            risk_amount DECIMAL(10, 2),
            timestamp BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_trade_id (trade_id),
            INDEX idx_event_type (event_type),
            INDEX idx_created_at (created_at)
        );
        """
        
        cursor.execute(create_table_sql)
        
        # Commit changes
        conn.commit()
        
        print("✅ Table created successfully!")
        
        # Verify table exists
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Table structure ({len(columns)} columns):")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Creating automated_signals table on Railway...")
    print(f"Database: {DATABASE_URL.split('@')[1]}\n")
    
    success = create_automated_signals_table()
    
    if success:
        print("\n🎉 Table is ready! Now run: python test_automated_webhook_system.py")
    else:
        print("\n⚠️  Table creation failed. Check the error above.")
