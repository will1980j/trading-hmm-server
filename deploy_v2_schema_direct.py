#!/usr/bin/env python3
"""
DEPLOY V2 SCHEMA DIRECTLY
Deploy the V2 database schema directly to Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def deploy_v2_schema():
    """Deploy V2 schema directly to Railway database"""
    try:
        # Get database URL
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        print("🔗 Connecting to Railway database...")
        
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Deploy V2 schema
        print("📊 Creating V2 database schema...")
        
        schema_sql = """
        -- Enhanced signals V2 table
        CREATE TABLE IF NOT EXISTS enhanced_signals_v2 (
            id SERIAL PRIMARY KEY,
            trade_uuid UUID DEFAULT gen_random_uuid(),
            signal_type VARCHAR(10) NOT NULL,
            session VARCHAR(20) NOT NULL,
            timestamp BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Signal Candle Data
            signal_candle_open DECIMAL(10,2),
            signal_candle_high DECIMAL(10,2),
            signal_candle_low DECIMAL(10,2),
            signal_candle_close DECIMAL(10,2),
            signal_candle_volume INTEGER,
            
            -- Confirmation Logic
            requires_confirmation BOOLEAN DEFAULT TRUE,
            confirmation_condition VARCHAR(50),
            confirmation_target_price DECIMAL(10,2),
            confirmation_received BOOLEAN DEFAULT FALSE,
            confirmation_timestamp BIGINT,
            
            -- Trade Execution
            entry_price DECIMAL(10,2),
            entry_timestamp BIGINT,
            stop_loss_price DECIMAL(10,2),
            stop_loss_scenario VARCHAR(50),
            stop_loss_reasoning TEXT,
            
            -- Pivot Analysis
            pivot_count INTEGER DEFAULT 0,
            signal_is_pivot BOOLEAN DEFAULT FALSE,
            pivot_data JSONB,
            
            -- R-Multiple Targets
            target_1r DECIMAL(10,2),
            target_2r DECIMAL(10,2),
            target_3r DECIMAL(10,2),
            target_5r DECIMAL(10,2),
            target_10r DECIMAL(10,2),
            target_20r DECIMAL(10,2),
            estimated_entry DECIMAL(10,2),
            risk_distance DECIMAL(10,2),
            
            -- MFE Tracking
            current_mfe DECIMAL(10,4) DEFAULT 0,
            max_mfe DECIMAL(10,4) DEFAULT 0,
            
            -- Status Tracking
            status VARCHAR(30) DEFAULT 'awaiting_confirmation',
            automation_level VARCHAR(20) DEFAULT 'enhanced_v2',
            resolved BOOLEAN DEFAULT FALSE,
            resolution_type VARCHAR(20),
            resolution_price DECIMAL(10,2),
            resolution_timestamp BIGINT,
            final_mfe DECIMAL(10,4),
            
            -- Data Storage
            market_context JSONB,
            raw_signal_data JSONB
        );
        
        -- Real-time price updates table
        CREATE TABLE IF NOT EXISTS realtime_prices (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL DEFAULT 'NQ',
            price DECIMAL(10,2) NOT NULL,
            timestamp BIGINT NOT NULL,
            session VARCHAR(20) NOT NULL,
            volume INTEGER DEFAULT 0,
            bid DECIMAL(10,2) DEFAULT 0,
            ask DECIMAL(10,2) DEFAULT 0,
            price_change DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Real-time MFE updates table
        CREATE TABLE IF NOT EXISTS realtime_mfe_updates (
            id SERIAL PRIMARY KEY,
            trade_uuid UUID NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            mfe_value DECIMAL(10,4) NOT NULL,
            is_new_high BOOLEAN DEFAULT FALSE,
            timestamp BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ V2 schema tables created")
        
        # Create indexes
        print("📈 Creating performance indexes...")
        
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_uuid ON enhanced_signals_v2(trade_uuid);
        CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_status ON enhanced_signals_v2(status);
        CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_timestamp ON enhanced_signals_v2(timestamp);
        CREATE INDEX IF NOT EXISTS idx_realtime_prices_timestamp ON realtime_prices(timestamp);
        CREATE INDEX IF NOT EXISTS idx_realtime_prices_symbol ON realtime_prices(symbol);
        CREATE INDEX IF NOT EXISTS idx_realtime_mfe_trade_uuid ON realtime_mfe_updates(trade_uuid);
        CREATE INDEX IF NOT EXISTS idx_realtime_mfe_timestamp ON realtime_mfe_updates(timestamp);
        """
        
        cursor.execute(indexes_sql)
        conn.commit()
        
        print("✅ Performance indexes created")
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('enhanced_signals_v2', 'realtime_prices', 'realtime_mfe_updates')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        table_names = [table['table_name'] for table in tables]
        
        print(f"✅ Verified tables: {table_names}")
        
        # Test insert to verify schema works
        print("🧪 Testing schema with sample data...")
        
        cursor.execute("""
            INSERT INTO enhanced_signals_v2 (
                signal_type, session, timestamp, signal_candle_close, status
            ) VALUES (
                'Bullish', 'NY AM', %s, 20500.00, 'test_schema'
            ) RETURNING id, trade_uuid;
        """, (int(datetime.now().timestamp() * 1000),))
        
        test_result = cursor.fetchone()
        test_id = test_result['id']
        test_uuid = test_result['trade_uuid']
        
        print(f"✅ Test record created: ID {test_id}, UUID {test_uuid}")
        
        # Clean up test record
        cursor.execute("DELETE FROM enhanced_signals_v2 WHERE id = %s", (test_id,))
        conn.commit()
        
        print("✅ Test record cleaned up")
        
        cursor.close()
        conn.close()
        
        print("\n🎯 V2 SCHEMA DEPLOYMENT COMPLETE!")
        print("Tables deployed:")
        for table in table_names:
            print(f"  ✅ {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema deployment failed: {str(e)}")
        return False

def main():
    """Main deployment function"""
    print("🚀 DEPLOYING V2 DATABASE SCHEMA")
    print("=" * 40)
    
    success = deploy_v2_schema()
    
    if success:
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("Your V2 backend database is ready for:")
        print("  📊 Enhanced signal processing")
        print("  📈 Real-time price tracking")
        print("  🎯 MFE monitoring")
        print("  🔄 Automated trade management")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("Check the error messages above")
    
    return success

if __name__ == "__main__":
    main()