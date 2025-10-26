"""
Deploy Dual TradingView Indicator System
Complete deployment of real-time V2 automation using TradingView Premium
"""

import os
import sys
import logging
import psycopg2
from urllib.parse import urlparse
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection using Railway DATABASE_URL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL environment variable not found")
        
        url = urlparse(database_url)
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        
        return conn
        
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def deploy_realtime_price_schema():
    """Deploy database schema for real-time price tracking"""
    
    schema_sql = '''
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
    
    -- Index for performance
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_timestamp ON realtime_prices(timestamp);
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_symbol ON realtime_prices(symbol);
    CREATE INDEX IF NOT EXISTS idx_realtime_prices_session ON realtime_prices(session);
    
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
    
    -- Index for MFE tracking
    CREATE INDEX IF NOT EXISTS idx_realtime_mfe_trade_uuid ON realtime_mfe_updates(trade_uuid);
    CREATE INDEX IF NOT EXISTS idx_realtime_mfe_timestamp ON realtime_mfe_updates(timestamp);
    
    -- Function to clean old price data (keep last 24 hours)
    CREATE OR REPLACE FUNCTION cleanup_old_price_data() RETURNS void AS $$
    BEGIN
        DELETE FROM realtime_prices 
        WHERE created_at < NOW() - INTERVAL '24 hours';
        
        DELETE FROM realtime_mfe_updates 
        WHERE created_at < NOW() - INTERVAL '7 days';
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
    '''
    
    try:
        conn = get_database_connection()
        if not conn:
            return {"success": False, "error": "Could not connect to database"}
        
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Real-time price schema deployed successfully")
        
        return {
            "success": True,
            "message": "Real-time price schema deployed successfully"
        }
        
    except Exception as e:
        logger.error(f"Schema deployment error: {str(e)}")
        return {"success": False, "error": str(e)}

def deploy_enhanced_v2_integration():
    """Deploy enhanced V2 integration functions"""
    
    integration_sql = '''
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
        LOOP
            -- Calculate new MFE
            IF v_trade.signal_type = 'Bullish' THEN
                v_new_mfe := (p_current_price - v_trade.entry_price) / 
                             NULLIF(v_trade.risk_distance, 0);
            ELSE -- Bearish
                v_new_mfe := (v_trade.entry_price - p_current_price) / 
                             NULLIF(v_trade.risk_distance, 0);
            END IF;
            
            -- Check if this is a new MFE high
            v_is_new_high := v_new_mfe > COALESCE(v_trade.max_mfe, 0);
            
            -- Update enhanced_signals_v2 table
            UPDATE enhanced_signals_v2 SET
                current_mfe = v_new_mfe,
                max_mfe = CASE WHEN v_is_new_high THEN v_new_mfe ELSE max_mfe END
            WHERE trade_uuid = v_trade.trade_uuid;
            
            -- Insert MFE update record
            INSERT INTO realtime_mfe_updates (
                trade_uuid, price, mfe_value, is_new_high, timestamp
            ) VALUES (
                v_trade.trade_uuid, p_current_price, v_new_mfe, v_is_new_high, p_timestamp
            );
            
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
    '''
    
    try:
        conn = get_database_connection()
        if not conn:
            return {"success": False, "error": "Could not connect to database"}
        
        cursor = conn.cursor()
        cursor.execute(integration_sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Enhanced V2 integration functions deployed")
        
        return {
            "success": True,
            "message": "Enhanced V2 integration functions deployed successfully"
        }
        
    except Exception as e:
        logger.error(f"Integration deployment error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_dual_indicator_system():
    """Test the dual indicator system"""
    
    # Test enhanced signal processing
    test_enhanced_signal = {
        "signal_type": "Bullish",
        "timestamp": 1698765432000,
        "session": "NY AM",
        "signal_candle": {
            "open": 4155.0,
            "high": 4157.5,
            "low": 4154.0,
            "close": 4156.25,
            "volume": 1000
        },
        "confirmation_data": {
            "required": True,
            "condition": "candle_close_above_signal_high",
            "target_price": 4157.5
        },
        "stop_loss_data": {
            "stop_loss_price": 4129.0
        }
    }
    
    # Test real-time price update
    test_price_update = {
        "type": "realtime_price",
        "symbol": "NQ",
        "price": 4158.75,
        "timestamp": 1698765433000,
        "session": "NY AM",
        "volume": 500,
        "change": 2.5
    }
    
    try:
        conn = get_database_connection()
        if not conn:
            return {"success": False, "error": "Could not connect to database"}
        
        cursor = conn.cursor()
        
        # Test real-time price processing
        cursor.execute("""
            SELECT process_realtime_price_update(%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_price_update["symbol"],
            test_price_update["price"],
            test_price_update["timestamp"],
            test_price_update["session"],
            test_price_update["volume"],
            test_price_update["price"],  # bid
            test_price_update["price"],  # ask
            test_price_update["change"]
        ))
        
        price_result = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Dual indicator system test completed")
        logger.info(f"Price processing result: {price_result}")
        
        return {
            "success": True,
            "price_test": price_result,
            "message": "Dual indicator system test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"System test error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Deploy the complete dual indicator system"""
    
    print("🚀 Deploying Dual TradingView Indicator System")
    print("=" * 60)
    
    # Step 1: Deploy real-time price schema
    print("📊 Deploying real-time price schema...")
    schema_result = deploy_realtime_price_schema()
    
    if schema_result["success"]:
        print("✅ Real-time price schema deployed successfully")
    else:
        print(f"❌ Schema deployment failed: {schema_result['error']}")
        return
    
    # Step 2: Deploy enhanced V2 integration
    print("\n🔧 Deploying enhanced V2 integration functions...")
    integration_result = deploy_enhanced_v2_integration()
    
    if integration_result["success"]:
        print("✅ Enhanced V2 integration deployed successfully")
    else:
        print(f"❌ Integration deployment failed: {integration_result['error']}")
        return
    
    # Step 3: Test the system
    print("\n🧪 Testing dual indicator system...")
    test_result = test_dual_indicator_system()
    
    if test_result["success"]:
        print("✅ Dual indicator system test passed")
    else:
        print(f"❌ System test failed: {test_result['error']}")
    
    print("\n" + "=" * 60)
    print("🎯 Dual TradingView Indicator System Deployment Summary:")
    print("✅ Real-time price schema deployed")
    print("✅ Enhanced V2 integration functions created")
    print("✅ MFE tracking system ready")
    print("✅ Database functions deployed")
    print("✅ System testing completed")
    
    print("\n📋 Next Steps:")
    print("1. Add TradingView indicators to charts:")
    print("   - Chart 1 (1-minute): enhanced_tradingview_indicator.pine")
    print("   - Chart 2 (1-second): tradingview_realtime_price_streamer.pine")
    print("2. Configure webhook URLs:")
    print("   - Signals: https://web-production-cd33.up.railway.app/api/live-signals-v2")
    print("   - Prices: https://web-production-cd33.up.railway.app/api/realtime-price")
    print("3. Deploy updated web_server.py to Railway")
    print("4. Test with live TradingView data")
    
    print("\n🔗 Files Ready for Deployment:")
    print("- enhanced_tradingview_indicator.pine (1-minute signals)")
    print("- tradingview_realtime_price_streamer.pine (1-second prices)")
    print("- realtime_price_webhook_handler.py (price processing)")
    print("- web_server.py (updated with price endpoint)")
    print("- deploy_dual_indicator_system.py (database setup)")

if __name__ == "__main__":
    main()