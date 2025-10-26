"""
Manual Schema Deployment for Dual Indicator System
Provides SQL scripts that can be run directly on Railway
"""

def get_dual_indicator_schema_sql():
    """Get the complete SQL schema for dual indicator system"""
    
    return '''
-- ============================================================================
-- DUAL TRADINGVIEW INDICATOR SYSTEM SCHEMA
-- Real-time price streaming + Enhanced signal processing
-- Run this SQL directly in Railway PostgreSQL console
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

def get_database_functions_sql():
    """Get the database functions SQL"""
    
    return '''
-- ============================================================================
-- DUAL INDICATOR SYSTEM DATABASE FUNCTIONS
-- Run this SQL after creating the tables above
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

def main():
    """Generate SQL files for manual deployment"""
    
    print("🚀 Generating SQL Files for Dual Indicator System")
    print("=" * 60)
    
    # Write schema SQL file
    with open('dual_indicator_schema.sql', 'w') as f:
        f.write(get_dual_indicator_schema_sql())
    
    # Write functions SQL file
    with open('dual_indicator_functions.sql', 'w') as f:
        f.write(get_database_functions_sql())
    
    print("✅ SQL files generated successfully:")
    print("   📄 dual_indicator_schema.sql - Database tables and indexes")
    print("   📄 dual_indicator_functions.sql - Database functions")
    
    print("\n📋 Manual Deployment Steps:")
    print("1. Go to Railway dashboard → Your project → PostgreSQL")
    print("2. Click 'Query' or 'Connect' to open database console")
    print("3. Run the contents of 'dual_indicator_schema.sql' first")
    print("4. Run the contents of 'dual_indicator_functions.sql' second")
    print("5. Verify tables were created with: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    
    print("\n🎯 Expected Tables After Deployment:")
    print("   - realtime_prices (1-second price updates)")
    print("   - enhanced_signals_v2 (comprehensive signal data)")
    print("   - realtime_mfe_updates (MFE tracking)")
    print("   - confirmation_monitor (confirmation tracking)")
    print("   - mfe_tracking (MFE history)")
    
    print("\n🚀 After Database Deployment:")
    print("1. Deploy updated web_server.py to Railway")
    print("2. Setup TradingView indicators with webhooks")
    print("3. Test real-time price streaming")
    
    # Also print the schema for immediate copy-paste
    print("\n" + "="*60)
    print("📋 COPY-PASTE SCHEMA (Run this in Railway PostgreSQL console):")
    print("="*60)
    print(get_dual_indicator_schema_sql())

if __name__ == "__main__":
    main()