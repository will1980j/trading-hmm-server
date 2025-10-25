-- =====================================================
-- SIGNAL LAB V2 - ENHANCED AUTOMATED TRADING SYSTEM
-- =====================================================
-- 
-- This is the next-generation Signal Lab with:
-- ✅ Automated price level calculations
-- ✅ Real-time MFE tracking  
-- ✅ Dynamic trade status management
-- ✅ Complete R-multiple system
-- ✅ Break-even automation support
-- 
-- Current Signal Lab remains untouched for production use
-- =====================================================

-- Enhanced Signal Lab V2 Table
CREATE TABLE signal_lab_v2_trades (
    -- Core Identity
    id BIGSERIAL PRIMARY KEY,
    trade_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    
    -- Signal Information (from TradingView)
    signal_timestamp TIMESTAMPTZ NOT NULL,
    signal_candle_time TIMESTAMPTZ,
    date DATE GENERATED ALWAYS AS (signal_timestamp::DATE) STORED,
    time TIME GENERATED ALWAYS AS (signal_timestamp::TIME) STORED,
    
    -- Trading Details
    symbol VARCHAR(10) DEFAULT 'NQ' NOT NULL,
    bias VARCHAR(20) NOT NULL CHECK (bias IN ('bullish', 'bearish')),
    session VARCHAR(20) NOT NULL CHECK (session IN ('ASIA', 'LONDON', 'NY PRE', 'NY AM', 'NY LUNCH', 'NY PM')),
    signal_type VARCHAR(50),
    
    -- 🎯 AUTOMATED PRICE LEVELS (The Holy Grail!)
    signal_candle_high DECIMAL(10,2),
    signal_candle_low DECIMAL(10,2),
    signal_candle_open DECIMAL(10,2),
    signal_candle_close DECIMAL(10,2),
    
    confirmation_candle_high DECIMAL(10,2),
    confirmation_candle_low DECIMAL(10,2),
    confirmation_candle_close DECIMAL(10,2),
    confirmation_timestamp TIMESTAMPTZ,
    
    entry_price DECIMAL(10,2),
    entry_timestamp TIMESTAMPTZ,
    
    -- Stop Loss Calculation Fields
    stop_loss_price DECIMAL(10,2),
    stop_loss_method VARCHAR(50), -- 'pivot_high', 'pivot_low', 'signal_candle', 'fallback_candle'
    pivot_candle_price DECIMAL(10,2),
    pivot_candle_timestamp TIMESTAMPTZ,
    
    -- R-Multiple System (Up to 20R for big trend moves)
    risk_distance DECIMAL(10,2), -- Entry to Stop Loss distance
    target_1r_price DECIMAL(10,2),
    target_2r_price DECIMAL(10,2),
    target_3r_price DECIMAL(10,2),
    target_4r_price DECIMAL(10,2),
    target_5r_price DECIMAL(10,2),
    target_6r_price DECIMAL(10,2),
    target_7r_price DECIMAL(10,2),
    target_8r_price DECIMAL(10,2),
    target_9r_price DECIMAL(10,2),
    target_10r_price DECIMAL(10,2),
    target_11r_price DECIMAL(10,2),
    target_12r_price DECIMAL(10,2),
    target_13r_price DECIMAL(10,2),
    target_14r_price DECIMAL(10,2),
    target_15r_price DECIMAL(10,2),
    target_16r_price DECIMAL(10,2),
    target_17r_price DECIMAL(10,2),
    target_18r_price DECIMAL(10,2),
    target_19r_price DECIMAL(10,2),
    target_20r_price DECIMAL(10,2),
    
    -- Break Even System
    breakeven_strategy VARCHAR(10) DEFAULT 'BE1' CHECK (breakeven_strategy IN ('BE1', 'NONE')),
    breakeven_trigger_price DECIMAL(10,2), -- +1R price level
    breakeven_achieved BOOLEAN DEFAULT FALSE,
    breakeven_timestamp TIMESTAMPTZ,
    
    -- 📊 DYNAMIC MFE TRACKING
    current_mfe DECIMAL(5,2) DEFAULT 0.00, -- Real-time MFE (updates continuously)
    max_mfe_price DECIMAL(10,2), -- Price level where max MFE occurred
    max_mfe_timestamp TIMESTAMPTZ,
    final_mfe DECIMAL(5,2), -- Final MFE when trade resolves
    
    -- Trade Status & Lifecycle
    trade_status VARCHAR(20) DEFAULT 'PENDING' CHECK (
        trade_status IN ('PENDING', 'CONFIRMED', 'ACTIVE', 'RESOLVED', 'CANCELLED')
    ),
    resolution_type VARCHAR(20) CHECK (
        resolution_type IN ('STOP_LOSS', 'BREAK_EVEN', 'TARGET_HIT', 'MANUAL_EXIT', 'CANCELLED')
    ),
    resolution_price DECIMAL(10,2),
    resolution_timestamp TIMESTAMPTZ,
    
    -- Position & Risk Management
    position_size INTEGER DEFAULT 1,
    risk_percentage DECIMAL(5,2) DEFAULT 1.00, -- % of account risked
    commission DECIMAL(6,2) DEFAULT 4.00,
    
    -- Market Context & News
    news_proximity VARCHAR(20),
    news_event TEXT,
    market_context JSONB, -- Store additional market data
    
    -- Automation Metadata
    auto_populated BOOLEAN DEFAULT FALSE, -- Was this trade auto-populated?
    validation_confidence DECIMAL(5,2), -- ML confidence score (future)
    manual_override BOOLEAN DEFAULT FALSE, -- Was automation overridden?
    override_reason TEXT,
    
    -- Legacy Compatibility (for migration)
    migrated_from_v1 BOOLEAN DEFAULT FALSE,
    v1_trade_id BIGINT, -- Reference to original signal_lab_trades.id
    
    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(50) DEFAULT 'system'
);

-- =====================================================
-- ACTIVE TRADES MONITORING TABLE
-- =====================================================
-- Separate table for real-time monitoring of active trades
-- Optimized for frequent MFE updates

CREATE TABLE active_trades_monitor (
    id BIGSERIAL PRIMARY KEY,
    trade_id BIGINT REFERENCES signal_lab_v2_trades(id) ON DELETE CASCADE,
    trade_uuid UUID REFERENCES signal_lab_v2_trades(trade_uuid) ON DELETE CASCADE,
    
    -- Current Market Data
    current_price DECIMAL(10,2) NOT NULL,
    current_mfe DECIMAL(5,2) NOT NULL,
    price_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- Monitoring Flags
    stop_loss_hit BOOLEAN DEFAULT FALSE,
    breakeven_triggered BOOLEAN DEFAULT FALSE,
    target_levels_hit JSONB, -- Track which targets hit: {"1R": true, "2R": false, ..., "20R": false}
    highest_target_hit INTEGER DEFAULT 0, -- Highest R-multiple target achieved (0-20)
    
    -- Performance Tracking
    unrealized_pnl DECIMAL(10,2),
    unrealized_r_multiple DECIMAL(5,2),
    
    -- Update Tracking
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    update_count INTEGER DEFAULT 1
);

-- =====================================================
-- SIGNAL VALIDATION QUEUE
-- =====================================================
-- Queue for processing incoming TradingView signals

CREATE TABLE signal_validation_queue (
    id BIGSERIAL PRIMARY KEY,
    signal_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    
    -- Raw Signal Data
    raw_signal_data JSONB NOT NULL,
    signal_timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) DEFAULT 'NQ',
    bias VARCHAR(20) NOT NULL,
    
    -- Validation Status
    validation_status VARCHAR(20) DEFAULT 'PENDING' CHECK (
        validation_status IN ('PENDING', 'VALID_SESSION', 'INVALID_SESSION', 'AWAITING_CONFIRMATION', 'CONFIRMED', 'CANCELLED', 'PROCESSED')
    ),
    session_classification VARCHAR(20),
    
    -- Confirmation Tracking
    awaiting_confirmation_since TIMESTAMPTZ,
    confirmation_deadline TIMESTAMPTZ, -- Optional timeout
    
    -- Processing Results
    processed_trade_id BIGINT REFERENCES signal_lab_v2_trades(id),
    rejection_reason TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Signal Lab V2 Indexes
CREATE INDEX idx_signal_lab_v2_date ON signal_lab_v2_trades(date DESC);
CREATE INDEX idx_signal_lab_v2_status ON signal_lab_v2_trades(trade_status);
CREATE INDEX idx_signal_lab_v2_session ON signal_lab_v2_trades(session);
CREATE INDEX idx_signal_lab_v2_symbol_date ON signal_lab_v2_trades(symbol, date DESC);
CREATE INDEX idx_signal_lab_v2_uuid ON signal_lab_v2_trades(trade_uuid);
CREATE INDEX idx_signal_lab_v2_auto ON signal_lab_v2_trades(auto_populated, created_at DESC);

-- Active Trades Indexes (optimized for real-time updates)
CREATE INDEX idx_active_trades_trade_id ON active_trades_monitor(trade_id);
CREATE INDEX idx_active_trades_uuid ON active_trades_monitor(trade_uuid);
CREATE INDEX idx_active_trades_updated ON active_trades_monitor(last_updated DESC);

-- Signal Queue Indexes
CREATE INDEX idx_signal_queue_status ON signal_validation_queue(validation_status);
CREATE INDEX idx_signal_queue_timestamp ON signal_validation_queue(signal_timestamp DESC);
CREATE INDEX idx_signal_queue_pending ON signal_validation_queue(validation_status, signal_timestamp) 
    WHERE validation_status IN ('PENDING', 'AWAITING_CONFIRMATION');

-- =====================================================
-- AUTOMATED UPDATE TRIGGERS
-- =====================================================

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_signal_lab_v2_updated_at 
    BEFORE UPDATE ON signal_lab_v2_trades 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_active_trades_updated_at 
    BEFORE UPDATE ON active_trades_monitor 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- DATA MIGRATION PREPARATION
-- =====================================================

-- View to compare V1 and V2 data during migration
CREATE VIEW signal_lab_migration_comparison AS
SELECT 
    v1.id as v1_id,
    v1.date as v1_date,
    v1.bias as v1_bias,
    v1.session as v1_session,
    v1.mfe as v1_mfe,
    v2.id as v2_id,
    v2.trade_uuid as v2_uuid,
    v2.final_mfe as v2_mfe,
    v2.auto_populated as v2_auto,
    v2.migrated_from_v1 as v2_migrated
FROM signal_lab_trades v1
LEFT JOIN signal_lab_v2_trades v2 ON v2.v1_trade_id = v1.id
ORDER BY v1.date DESC, v1.time DESC;

-- =====================================================
-- COMMENTS & DOCUMENTATION
-- =====================================================

COMMENT ON TABLE signal_lab_v2_trades IS 'Enhanced Signal Lab with automated price calculations and real-time MFE tracking';
COMMENT ON TABLE active_trades_monitor IS 'Real-time monitoring table for active trades with frequent MFE updates';
COMMENT ON TABLE signal_validation_queue IS 'Processing queue for incoming TradingView signals with session validation';

COMMENT ON COLUMN signal_lab_v2_trades.trade_uuid IS 'Unique identifier for cross-system trade tracking';
COMMENT ON COLUMN signal_lab_v2_trades.current_mfe IS 'Real-time MFE that updates continuously for active trades';
COMMENT ON COLUMN signal_lab_v2_trades.final_mfe IS 'Final MFE value when trade resolves (static)';
COMMENT ON COLUMN signal_lab_v2_trades.auto_populated IS 'TRUE if trade was created by automation system';
COMMENT ON COLUMN signal_lab_v2_trades.risk_distance IS 'Distance from entry to stop loss in price points';
COMMENT ON COLUMN signal_lab_v2_trades.target_20r_price IS 'Ultimate target for major trend moves - 20x risk distance from entry';

-- =====================================================
-- R-MULTIPLE CALCULATION FUNCTIONS
-- =====================================================

-- Function to calculate all R-multiple targets for a trade
CREATE OR REPLACE FUNCTION calculate_r_targets(
    entry_price DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    is_bullish BOOLEAN
) RETURNS JSONB AS $$
DECLARE
    risk_distance DECIMAL(10,2);
    targets JSONB := '{}';
    i INTEGER;
BEGIN
    -- Calculate risk distance
    risk_distance := ABS(entry_price - stop_loss_price);
    
    -- Calculate all 20 R-multiple targets
    FOR i IN 1..20 LOOP
        IF is_bullish THEN
            targets := targets || jsonb_build_object(
                CONCAT(i, 'R'), 
                entry_price + (i * risk_distance)
            );
        ELSE
            targets := targets || jsonb_build_object(
                CONCAT(i, 'R'), 
                entry_price - (i * risk_distance)
            );
        END IF;
    END LOOP;
    
    -- Add risk distance and break even info
    targets := targets || jsonb_build_object(
        'risk_distance', risk_distance,
        'break_even_trigger', targets->'1R',
        'entry_price', entry_price,
        'stop_loss_price', stop_loss_price
    );
    
    RETURN targets;
END;
$$ LANGUAGE plpgsql;

-- Function to update MFE based on current price
CREATE OR REPLACE FUNCTION calculate_current_mfe(
    entry_price DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    is_bullish BOOLEAN
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    risk_distance DECIMAL(10,2);
    mfe DECIMAL(5,2);
BEGIN
    risk_distance := ABS(entry_price - stop_loss_price);
    
    IF is_bullish THEN
        -- For bullish trades, MFE is how far above entry we've gone
        mfe := (current_price - entry_price) / risk_distance;
    ELSE
        -- For bearish trades, MFE is how far below entry we've gone
        mfe := (entry_price - current_price) / risk_distance;
    END IF;
    
    -- MFE can't be negative (that would be drawdown)
    RETURN GREATEST(mfe, 0.00);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
-- If you see this message, the Signal Lab V2 schema was created successfully!
-- ✅ Enhanced with 20R targeting system for major trend moves
-- ✅ Automated R-multiple calculation functions included
-- Ready for Phase 2: Price Data Integration & Automation Engine
-- =====================================================