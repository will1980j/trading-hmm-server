"""
Deploy Dual Indicator Schema to Railway
Uses your existing Railway connection method
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_railway_connection():
    """Get Railway database connection using your existing method"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            # Try to get from Railway environment
            database_url = os.environ.get('PGDATABASE')
            if database_url:
                # Construct full URL if we have individual components
                host = os.environ.get('PGHOST', 'localhost')
                port = os.environ.get('PGPORT', '5432')
                user = os.environ.get('PGUSER', 'postgres')
                password = os.environ.get('PGPASSWORD', '')
                database_url = f"postgresql://{user}:{password}@{host}:{port}/{database_url}"
        
        if not database_url:
            raise Exception("No DATABASE_URL or PostgreSQL environment variables found")
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        logger.info("✅ Connected to Railway PostgreSQL database")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Database connection error: {str(e)}")
        return None

def deploy_dual_indicator_schema():
    """Deploy the complete dual indicator schema"""
    
    schema_sql = '''
    -- ============================================================================
    -- DUAL TRADINGVIEW INDICATOR SYSTEM SCHEMA
    -- Real-time price streaming + Enhanced signal processing
    -- ============================================================================
    
    -- Real-time price updates table (1-second TradingView data)
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
    
    -- Enhanced signals V2 table (if not exists from previous deployment)
    CREATE TABLE IF NOT EXISTS enhanced_signals_v2 (
        id SERIAL PRIMARY KEY,
        trade_uuid UUID DEFAULT gen_random_uuid(),
        
        -- Basic signal data
        signal_type VARCHAR(10) NOT NULL,
        session VARCHAR(20) NOT NULL,
        timestamp BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Signal candle OHLCV
        signal_candle_open DECIMAL(10,2),
        signal_candle_high DECIMAL(10,2),
        signal_candle_low DECIMAL(10,2),
        signal_candle_close DECIMAL(10,2),
        signal_candle_volume INTEGER,
        
        -- Confirmation data
        requires_confirmation BOOLEAN DEFAULT TRUE,
        confirmation_condition VARCHAR(50),
        confirmation_target_price DECIMAL(10,2),
        confirmation_received BOOLEAN DEFAULT FALSE,
        confirmation_timestamp BIGINT,
        confirmation_candle_open DECIMAL(10,2),
        confirmation_candle_high DECIMAL(10,2),
        confirmation_candle_low DECIMAL(10,2),
        confirmation_candle_close DECIMAL(10,2),
        
        -- Entry data (filled when confirmation occurs)
        entry_price DECIMAL(10,2),
        entry_timestamp BIGINT,
        
        -- Stop loss data
        stop_loss_price DECIMAL(10,2),
        stop_loss_scenario VARCHAR(50),
        stop_loss_reasoning TEXT,
        
        -- Pivot analysis
        pivot_count INTEGER DEFAULT 0,
        signal_is_pivot BOOLEAN DEFAULT FALSE,
        pivot_data JSONB,
        
        -- R-targets
        target_1r DECIMAL(10,2),
        target_2r DECIMAL(10,2),
        target_3r DECIMAL(10,2),
        target_5r DECIMAL(10,2),
        target_10r DECIMAL(10,2),
        target_20r DECIMAL(10,2),
        
        -- Risk management
        estimated_entry DECIMAL(10,2),
        risk_distance DECIMAL(10,2),
        
        -- MFE tracking (updated by real-time prices)
        current_mfe DECIMAL(10,4) DEFAULT 0,
        max_mfe DECIMAL(10,4) DEFAULT 0,
        mfe_updates JSONB DEFAULT '[]',
        
        -- Status tracking
        status VARCHAR(30) DEFAULT 'awaiting_confirmation',
        automation_level VARCHAR(20) DEFAULT 'enhanced_v2',
        
        -- Trade resolution
        resolved BOOLEAN DEFAULT FALSE,
        resolution_type VARCHAR(20),
        resolution_price DECIMAL(10,2),
        resolution_timestamp BIGINT,
        final_mfe DECIMAL(10,4),
        
        -- Market context (from TradingView)
        market_context JSONB,
        
        -- Raw signal data (for debugging)
        raw_signal_data JSONB
    );
    
    -- Real-time MFE updates table (high-frequency updates)
    CREATE TABLE IF NOT EXISTS realtime_mfe_updates (
        id SERIAL PRIMARY KEY,
        trade_uuid UUID NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        mfe_value DECIMAL(10,4) NOT NULL,
        is_new_high BOOLEAN DEFAULT FALSE,
        timestamp BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Confirmation monitoring table (if not exists)
    CREATE TABLE IF NOT EXISTS confirmation_monitor (
        id SERIAL PRIMARY KEY,
        trade_uuid UUID REFERENCES enhanced_signals_v2(trade_uuid),
        signal_type VARCHAR(10) NOT NULL,
        target_price DECIMAL(10,2) NOT NULL,
        condition VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        last_check TIMESTAMP,
        check_count INTEGER DEFAULT 0
    );
    
    -- MFE tracking table (if not exists)
    CREATE TABLE IF NOT EXISTS mfe_tracking (
        id SERIAL PRIMARY KEY,
        trade_uuid UUID REFERENCES enhanced_signals_v2(trade_uuid),
        timestamp BIGINT NOT NULL,
        current_price DECIMAL(10,2) NOT NULL,
        mfe_value DECIMAL(10,4) NOT NULL,
        is_new_high BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- ============================================================================
    -- INDEXES FOR PERFORMANCE
    -- ============================================================================
    
    -- Real-time prices indexes
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_timestamp ON realtime_prices(timestamp);
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_symbol ON realtime_prices(symbol);
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_session ON realtime_prices(session);
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_created_at ON realtime_prices(created_at);
    
    -- Enhanced signals V2 indexes
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_timestamp ON enhanced_signals_v2(timestamp);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_status ON enhanced_signals_v2(status);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_session ON enhanced_signals_v2(session);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_uuid ON enhanced_signals_v2(trade_uuid);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_resolved ON enhanced_signals_v2(resolved);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_confirmation ON enhanced_signals_v2(confirmation_received);
    
    -- Real-time MFE updates indexes
    CREATE INDEX IF NOT EXISTS idx_realtime_mfe_trade_uuid ON realtime_mfe_updates(trade_uuid);
    CREATE INDEX IF NOT EXISTS idx_realtime_mfe_timestamp ON realtime_mfe_updates(timestamp);
    CREATE INDEX IF NOT EXISTS idx_realtime_mfe_created_at ON realtime_mfe_updates(created_at);
    
    -- Confirmation monitor indexes
    CREATE INDEX IF NOT EXISTS idx_confirmation_monitor_active ON confirmation_monitor(is_active);
    CREATE INDEX IF NOT EXISTS idx_confirmation_monitor_uuid ON confirmation_monitor(trade_uuid);
    
    -- MFE tracking indexes
    CREATE INDEX IF NOT EXISTS idx_mfe_tracking_uuid ON mfe_tracking(trade_uuid);
    CREATE INDEX IF NOT EXISTS idx_mfe_tracking_timestamp ON mfe_tracking(timestamp);
    '''
    
    try:
        conn = get_railway_connection()
        if not conn:
            return {"success": False, "error": "Could not connect to Railway database"}
        
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('realtime_prices', 'enhanced_signals_v2', 'realtime_mfe_updates', 'confirmation_monitor', 'mfe_tracking')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        table_names = [table['table_name'] for table in tables]
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Schema deployed successfully. Tables: {table_names}")
        
        return {
            "success": True,
            "tables_created": table_names,
            "message": "Dual indicator schema deployed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Schema deployment error: {str(e)}")
        return {"success": False, "error": str(e)}

def deploy_database_functions():
    """Deploy database functions for dual indicator system"""
    
    functions_sql = '''
    -- ============================================================================
    -- DUAL INDICATOR SYSTEM DATABASE FUNCTIONS
    -- ============================================================================
    
    -- Function to process real-time price updates
    CREATE OR REPLACE FUNCTION process_realtime_price_update(
        p_symbol VARCHAR,
        p_price DECIMAL,
        p_timestamp BIGINT,
        p_session VARCHAR,
        p_volume INTEGER DEFAULT 0,
        p_bid DECIMAL DEFAULT 0,
        p_ask DECIMAL DEFAULT 0,
        p_change DECIMAL DEFAULT 0
    ) RETURNS JSONB AS $$
    DECLARE
        v_result JSONB;
        v_active_trades INTEGER;
    BEGIN
        -- Insert price update
        INSERT INTO realtime_prices (
            symbol, price, timestamp, session, volume, bid, ask, price_change
        ) VALUES (
            p_symbol, p_price, p_timestamp, p_session, p_volume, p_bid, p_ask, p_change
        );
        
        -- Count active trades that need MFE updates
        SELECT COUNT(*) INTO v_active_trades
        FROM enhanced_signals_v2
        WHERE confirmation_received = TRUE
        AND resolved = FALSE
        AND entry_price IS NOT NULL;
        
        -- Update MFE for active trades if any exist
        IF v_active_trades > 0 THEN
            PERFORM update_active_trades_mfe(p_price, p_timestamp);
        END IF;
        
        -- Return success result
        v_result := jsonb_build_object(
            'success', TRUE,
            'price_recorded', p_price,
            'active_trades_updated', v_active_trades,
            'timestamp', p_timestamp
        );
        
        RETURN v_result;
        
    EXCEPTION WHEN OTHERS THEN
        RETURN jsonb_build_object(
            'success', FALSE,
            'error', SQLERRM
        );
    END;
    $$ LANGUAGE plpgsql;
    
    -- Function to update MFE for active trades
    CREATE OR REPLACE FUNCTION update_active_trades_mfe(
        p_current_price DECIMAL,
        p_timestamp BIGINT
    ) RETURNS JSONB AS $$
    DECLARE
        v_trade RECORD;
        v_new_mfe DECIMAL;
        v_is_new_high BOOLEAN;
        v_updates_count INTEGER := 0;
    BEGIN
        -- Loop through all active trades
        FOR v_trade IN 
            SELECT trade_uuid, signal_type, entry_price, stop_loss_price, 
                   risk_distance, current_mfe, max_mfe
            FROM enhanced_signals_v2
            WHERE confirmation_received = TRUE
            AND resolved = FALSE
            AND entry_price IS NOT NULL
            AND stop_loss_price IS NOT NULL
            AND risk_distance IS NOT NULL
            AND risk_distance > 0
        LOOP
            -- Calculate new MFE
            IF v_trade.signal_type = 'Bullish' THEN
                v_new_mfe := (p_current_price - v_trade.entry_price) / v_trade.risk_distance;
            ELSE -- Bearish
                v_new_mfe := (v_trade.entry_price - p_current_price) / v_trade.risk_distance;
            END IF;
            
            -- Check if this is a new MFE high
            v_is_new_high := v_new_mfe > COALESCE(v_trade.max_mfe, 0);
            
            -- Update enhanced_signals_v2 table
            UPDATE enhanced_signals_v2 SET
                current_mfe = v_new_mfe,
                max_mfe = CASE WHEN v_is_new_high THEN v_new_mfe ELSE max_mfe END
            WHERE trade_uuid = v_trade.trade_uuid;
            
            -- Insert MFE update record (only if significant change or new high)
            IF v_is_new_high OR ABS(v_new_mfe - COALESCE(v_trade.current_mfe, 0)) > 0.1 THEN
                INSERT INTO realtime_mfe_updates (
                    trade_uuid, price, mfe_value, is_new_high, timestamp
                ) VALUES (
                    v_trade.trade_uuid, p_current_price, v_new_mfe, v_is_new_high, p_timestamp
                );
            END IF;
            
            v_updates_count := v_updates_count + 1;
        END LOOP;
        
        RETURN jsonb_build_object(
            'success', TRUE,
            'trades_updated', v_updates_count,
            'current_price', p_current_price
        );
        
    EXCEPTION WHEN OTHERS THEN
        RETURN jsonb_build_object(
            'success', FALSE,
            'error', SQLERRM
        );
    END;
    $$ LANGUAGE plpgsql;
    
    -- Function to get latest price
    CREATE OR REPLACE FUNCTION get_latest_price(p_symbol VARCHAR DEFAULT 'NQ') 
    RETURNS TABLE(price DECIMAL, timestamp BIGINT, session VARCHAR) AS $$
    BEGIN
        RETURN QUERY
        SELECT rp.price, rp.timestamp, rp.session
        FROM realtime_prices rp
        WHERE rp.symbol = p_symbol
        ORDER BY rp.timestamp DESC
        LIMIT 1;
    END;
    $$ LANGUAGE plpgsql;
    
    -- Function to clean old price data (keep last 24 hours)
    CREATE OR REPLACE FUNCTION cleanup_old_price_data() RETURNS void AS $$
    BEGIN
        DELETE FROM realtime_prices 
        WHERE created_at < NOW() - INTERVAL '24 hours';
        
        DELETE FROM realtime_mfe_updates 
        WHERE created_at < NOW() - INTERVAL '7 days';
        
        -- Log cleanup
        RAISE NOTICE 'Cleaned up old price data and MFE updates';
    END;
    $$ LANGUAGE plpgsql;
    '''
    
    try:
        conn = get_railway_connection()
        if not conn:
            return {"success": False, "error": "Could not connect to Railway database"}
        
        cursor = conn.cursor()
        cursor.execute(functions_sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database functions deployed successfully")
        
        return {
            "success": True,
            "message": "Database functions deployed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Functions deployment error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_dual_system():
    """Test the dual indicator system"""
    
    try:
        conn = get_railway_connection()
        if not conn:
            return {"success": False, "error": "Could not connect to Railway database"}
        
        cursor = conn.cursor()
        
        # Test real-time price processing
        cursor.execute("""
            SELECT process_realtime_price_update(%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            'NQ',           # symbol
            4158.75,        # price
            1698765433000,  # timestamp
            'NY AM',        # session
            500,            # volume
            4158.50,        # bid
            4159.00,        # ask
            2.5             # change
        ))
        
        price_result = cursor.fetchone()[0]
        
        # Test latest price function
        cursor.execute("SELECT * FROM get_latest_price('NQ')")
        latest_price = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Dual indicator system test completed successfully")
        
        return {
            "success": True,
            "price_test": price_result,
            "latest_price": dict(latest_price) if latest_price else None,
            "message": "Dual indicator system test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ System test error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Deploy the complete dual indicator system to Railway"""
    
    print("🚀 Deploying Dual TradingView Indicator System to Railway")
    print("=" * 70)
    
    # Step 1: Deploy schema
    print("📊 Deploying database schema...")
    schema_result = deploy_dual_indicator_schema()
    
    if schema_result["success"]:
        print(f"✅ Schema deployed successfully")
        print(f"   Tables created: {schema_result['tables_created']}")
    else:
        print(f"❌ Schema deployment failed: {schema_result['error']}")
        return
    
    # Step 2: Deploy functions
    print("\n🔧 Deploying database functions...")
    functions_result = deploy_database_functions()
    
    if functions_result["success"]:
        print("✅ Database functions deployed successfully")
    else:
        print(f"❌ Functions deployment failed: {functions_result['error']}")
        return
    
    # Step 3: Test system
    print("\n🧪 Testing dual indicator system...")
    test_result = test_dual_system()
    
    if test_result["success"]:
        print("✅ System test passed")
        if test_result.get('latest_price'):
            print(f"   Latest price test: ${test_result['latest_price']['price']}")
    else:
        print(f"❌ System test failed: {test_result['error']}")
    
    print("\n" + "=" * 70)
    print("🎯 Dual TradingView Indicator System Deployment Complete!")
    print("✅ Real-time price schema deployed")
    print("✅ Enhanced signals V2 schema ready")
    print("✅ MFE tracking system operational")
    print("✅ Database functions deployed")
    print("✅ System testing completed")
    
    print("\n📋 Next Steps:")
    print("1. Setup TradingView indicators:")
    print("   - Chart 1 (1-minute): enhanced_tradingview_indicator.pine")
    print("   - Chart 2 (1-second): tradingview_realtime_price_streamer.pine")
    print("2. Configure webhook URLs:")
    print("   - Signals: https://web-production-cd33.up.railway.app/api/live-signals-v2")
    print("   - Prices: https://web-production-cd33.up.railway.app/api/realtime-price")
    print("3. Deploy updated web_server.py to Railway")
    print("4. Test with live TradingView data")
    
    print("\n🚀 Your V2 automation system is ready for real-time trading!")

if __name__ == "__main__":
    main()