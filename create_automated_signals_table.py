"""
Create automated_signals table in Railway database
"""

import os
from database.railway_db import RailwayDB

def create_automated_signals_table():
    """Create the automated_signals table"""
    
    print("🚀 Creating automated_signals table...")
    
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        # Create table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS automated_signals (
            id SERIAL PRIMARY KEY,
            trade_id VARCHAR(100),
            event_type VARCHAR(20),
            direction VARCHAR(10),
            entry_price DECIMAL(10,2),
            stop_loss DECIMAL(10,2),
            session VARCHAR(20),
            bias VARCHAR(20),
            risk_distance DECIMAL(10,2),
            targets JSONB,
            current_price DECIMAL(10,2),
            mfe DECIMAL(10,4),
            exit_price DECIMAL(10,2),
            final_mfe DECIMAL(10,4),
            timestamp TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_automated_signals_trade_id ON automated_signals(trade_id);
        CREATE INDEX IF NOT EXISTS idx_automated_signals_event_type ON automated_signals(event_type);
        CREATE INDEX IF NOT EXISTS idx_automated_signals_timestamp ON automated_signals(timestamp);
        """
        
        cursor.execute(create_table_sql)
        db.conn.commit()
        
        print("✅ Table created successfully!")
        
        # Verify table exists
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        print(f"\n📋 Table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
        
        cursor.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        return False


if __name__ == "__main__":
    success = create_automated_signals_table()
    
    if success:
        print("\n🎉 Database is ready for automated signals!")
        print("\nRun the test again:")
        print("   python test_automated_webhook_system.py")
    else:
        print("\n⚠️  Table creation failed. Check the error above.")
