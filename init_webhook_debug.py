"""Initialize Webhook Debug Tables"""
import sys
from database.railway_db import RailwayDB

def init_webhook_debug_tables():
    """Create webhook debugging tables"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("Creating webhook debug tables...")
        
        # Create webhook_debug_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_debug_log (
                id SERIAL PRIMARY KEY,
                raw_payload TEXT,
                parsed_data JSONB,
                source VARCHAR(50) DEFAULT 'TradingView',
                received_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ webhook_debug_log table created")
        
        # Create signal_processing_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_processing_log (
                id SERIAL PRIMARY KEY,
                bias VARCHAR(20),
                symbol VARCHAR(20),
                price DECIMAL(10, 4),
                status VARCHAR(20),
                error_message TEXT,
                processed_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ signal_processing_log table created")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_webhook_debug_received 
            ON webhook_debug_log(received_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signal_processing_bias 
            ON signal_processing_log(bias, processed_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signal_processing_status 
            ON signal_processing_log(status, processed_at DESC)
        """)
        print("✅ Indexes created")
        
        # Create view
        cursor.execute("""
            CREATE OR REPLACE VIEW signal_stats_24h AS
            SELECT 
                bias,
                COUNT(*) as total_signals,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                MAX(processed_at) as last_signal
            FROM signal_processing_log
            WHERE processed_at > NOW() - INTERVAL '24 hours'
            GROUP BY bias
        """)
        print("✅ signal_stats_24h view created")
        
        db.conn.commit()
        print("\n✅ Webhook debug tables initialized successfully!")
        
        # Test query
        cursor.execute("SELECT COUNT(*) as count FROM webhook_debug_log")
        count = cursor.fetchone()['count']
        print(f"\nCurrent webhook logs: {count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM signal_processing_log")
        count = cursor.fetchone()['count']
        print(f"Current signal processing logs: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing webhook debug tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_webhook_debug_tables()
    sys.exit(0 if success else 1)
