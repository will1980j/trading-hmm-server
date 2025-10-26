
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
