-- ============================================================================
-- FULL AUTOMATION DATABASE SCHEMA
-- Supports complete automated trading pipeline with exact methodology
-- ============================================================================

-- Table for tracking pending signals awaiting confirmation
CREATE TABLE IF NOT EXISTS pending_signals (
    id SERIAL PRIMARY KEY,
    signal_id VARCHAR(255) UNIQUE NOT NULL,
    signal_type VARCHAR(20) NOT NULL, -- 'Bullish' or 'Bearish'
    timestamp BIGINT NOT NULL,
    session VARCHAR(20) NOT NULL, -- 'ASIA', 'LONDON', 'NY_AM', etc.
    
    -- Signal candle data
    signal_open DECIMAL(10,2),
    signal_high DECIMAL(10,2),
    signal_low DECIMAL(10,2),
    signal_close DECIMAL(10,2),
    signal_volume BIGINT,
    
    -- Previous candle data
    previous_open DECIMAL(10,2),
    previous_high DECIMAL(10,2),
    previous_low DECIMAL(10,2),
    previous_close DECIMAL(10,2),
    
    -- Market context
    atr DECIMAL(10,4),
    volatility DECIMAL(10,4),
    signal_strength DECIMAL(5,2),
    
    -- FVG data
    bias VARCHAR(20),
    htf_status TEXT,
    fvg_signal_type VARCHAR(50),
    htf_aligned BOOLEAN,
    
    -- Methodology data
    requires_confirmation BOOLEAN DEFAULT TRUE,
    stop_loss_buffer INTEGER DEFAULT 25,
    
    -- Automation tracking
    automation_stage VARCHAR(50) NOT NULL, -- 'SIGNAL_DETECTED', 'CONFIRMATION_DETECTED', etc.
    
    -- Confirmation data (populated when confirmed)
    confirmation_timestamp BIGINT,
    confirmation_open DECIMAL(10,2),
    confirmation_high DECIMAL(10,2),
    confirmation_low DECIMAL(10,2),
    confirmation_close DECIMAL(10,2),
    
    -- Calculated trade parameters
    calculated_entry_price DECIMAL(10,2),
    calculated_stop_loss DECIMAL(10,2),
    risk_distance DECIMAL(10,2),
    
    -- Actual execution data
    actual_entry_price DECIMAL(10,2),
    actual_entry_timestamp BIGINT,
    initial_mfe DECIMAL(8,4),
    
    -- Final outcome
    final_outcome DECIMAL(8,4), -- Final R-multiple result
    final_mfe DECIMAL(8,4),
    resolution_timestamp BIGINT,
    
    -- Cancellation data
    cancellation_reason VARCHAR(100),
    cancellation_timestamp BIGINT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enhanced Signal Lab V2 table with automation support
CREATE TABLE IF NOT EXISTS signal_lab_v2_trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(255) UNIQUE NOT NULL,
    signal_type VARCHAR(20) NOT NULL, -- 'Bullish' or 'Bearish'
    timestamp BIGINT NOT NULL,
    session VARCHAR(20) NOT NULL,
    
    -- Price data
    signal_price DECIMAL(10,2) NOT NULL, -- Original signal candle close
    entry_price DECIMAL(10,2) NOT NULL,  -- Actual entry price
    stop_loss_price DECIMAL(10,2) NOT NULL,
    risk_distance DECIMAL(10,2) NOT NULL,
    
    -- MFE tracking
    current_mfe DECIMAL(8,4) DEFAULT 0.0,
    max_mfe DECIMAL(8,4) DEFAULT 0.0,
    last_mfe_update BIGINT,
    
    -- Trade status
    trade_status VARCHAR(20) DEFAULT 'ACTIVE', -- 'ACTIVE', 'STOPPED_OUT', 'BREAK_EVEN'
    outcome_r DECIMAL(8,4), -- Final R-multiple outcome
    final_mfe DECIMAL(8,4),
    
    -- Resolution data
    resolution_type VARCHAR(20), -- 'STOP_LOSS', 'BREAK_EVEN'
    resolution_timestamp BIGINT,
    resolution_price DECIMAL(10,2),
    resolved_at TIMESTAMP,
    
    -- Source tracking
    automation_source VARCHAR(50) DEFAULT 'MANUAL', -- 'MANUAL', 'FULL_AUTOMATION'
    
    -- Market context (from original signal)
    signal_strength DECIMAL(5,2),
    htf_aligned BOOLEAN,
    fvg_signal_type VARCHAR(50),
    atr DECIMAL(10,4),
    volatility DECIMAL(10,4),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table for tracking automation performance metrics
CREATE TABLE IF NOT EXISTS automation_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    
    -- Signal metrics
    total_signals INTEGER DEFAULT 0,
    confirmed_signals INTEGER DEFAULT 0,
    cancelled_signals INTEGER DEFAULT 0,
    confirmation_rate DECIMAL(5,2),
    
    -- Trade metrics
    total_trades INTEGER DEFAULT 0,
    stopped_out_trades INTEGER DEFAULT 0,
    break_even_trades INTEGER DEFAULT 0,
    active_trades INTEGER DEFAULT 0,
    
    -- Performance metrics
    total_r_outcome DECIMAL(10,4) DEFAULT 0.0,
    average_mfe DECIMAL(8,4) DEFAULT 0.0,
    max_mfe_achieved DECIMAL(8,4) DEFAULT 0.0,
    
    -- Session breakdown
    asia_signals INTEGER DEFAULT 0,
    london_signals INTEGER DEFAULT 0,
    ny_am_signals INTEGER DEFAULT 0,
    ny_lunch_signals INTEGER DEFAULT 0,
    ny_pm_signals INTEGER DEFAULT 0,
    
    -- Automation health
    webhook_success_rate DECIMAL(5,2),
    processing_errors INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pending_signals_stage ON pending_signals(automation_stage);
CREATE INDEX IF NOT EXISTS idx_pending_signals_timestamp ON pending_signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_pending_signals_session ON pending_signals(session);

CREATE INDEX IF NOT EXISTS idx_v2_trades_status ON signal_lab_v2_trades(trade_status);
CREATE INDEX IF NOT EXISTS idx_v2_trades_timestamp ON signal_lab_v2_trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_v2_trades_session ON signal_lab_v2_trades(session);
CREATE INDEX IF NOT EXISTS idx_v2_trades_automation ON signal_lab_v2_trades(automation_source);

CREATE INDEX IF NOT EXISTS idx_automation_metrics_date ON automation_metrics(date);

-- Views for easy querying
CREATE OR REPLACE VIEW automation_dashboard AS
SELECT 
    ps.automation_stage,
    COUNT(*) as count,
    AVG(ps.signal_strength) as avg_signal_strength,
    COUNT(CASE WHEN ps.htf_aligned THEN 1 END) as htf_aligned_count,
    MAX(ps.created_at) as latest_signal
FROM pending_signals ps
WHERE ps.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY ps.automation_stage;

CREATE OR REPLACE VIEW active_trades_summary AS
SELECT 
    t.trade_id,
    t.signal_type,
    t.session,
    t.entry_price,
    t.stop_loss_price,
    t.current_mfe,
    t.max_mfe,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_active,
    t.created_at
FROM signal_lab_v2_trades t
WHERE t.trade_status = 'ACTIVE'
ORDER BY t.created_at DESC;

CREATE OR REPLACE VIEW automation_performance AS
SELECT 
    DATE(t.created_at) as trade_date,
    t.session,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN t.trade_status = 'STOPPED_OUT' THEN 1 END) as stopped_out,
    COUNT(CASE WHEN t.trade_status = 'BREAK_EVEN' THEN 1 END) as break_even,
    SUM(COALESCE(t.outcome_r, 0)) as total_r_outcome,
    AVG(t.max_mfe) as avg_max_mfe,
    MAX(t.max_mfe) as best_mfe
FROM signal_lab_v2_trades t
WHERE t.automation_source = 'FULL_AUTOMATION'
  AND t.created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(t.created_at), t.session
ORDER BY trade_date DESC, t.session;

-- Function to update automation metrics daily
CREATE OR REPLACE FUNCTION update_automation_metrics()
RETURNS VOID AS $$
DECLARE
    target_date DATE := CURRENT_DATE;
BEGIN
    INSERT INTO automation_metrics (
        date, total_signals, confirmed_signals, cancelled_signals,
        total_trades, stopped_out_trades, break_even_trades, active_trades,
        total_r_outcome, average_mfe, max_mfe_achieved,
        asia_signals, london_signals, ny_am_signals, ny_lunch_signals, ny_pm_signals
    )
    SELECT 
        target_date,
        COUNT(*) as total_signals,
        COUNT(CASE WHEN automation_stage IN ('CONFIRMATION_DETECTED', 'TRADE_ACTIVATED', 'TRADE_RESOLVED') THEN 1 END),
        COUNT(CASE WHEN automation_stage = 'SIGNAL_CANCELLED' THEN 1 END),
        (SELECT COUNT(*) FROM signal_lab_v2_trades WHERE DATE(created_at) = target_date AND automation_source = 'FULL_AUTOMATION'),
        (SELECT COUNT(*) FROM signal_lab_v2_trades WHERE DATE(created_at) = target_date AND automation_source = 'FULL_AUTOMATION' AND trade_status = 'STOPPED_OUT'),
        (SELECT COUNT(*) FROM signal_lab_v2_trades WHERE DATE(created_at) = target_date AND automation_source = 'FULL_AUTOMATION' AND trade_status = 'BREAK_EVEN'),
        (SELECT COUNT(*) FROM signal_lab_v2_trades WHERE automation_source = 'FULL_AUTOMATION' AND trade_status = 'ACTIVE'),
        (SELECT COALESCE(SUM(outcome_r), 0) FROM signal_lab_v2_trades WHERE DATE(created_at) = target_date AND automation_source = 'FULL_AUTOMATION'),
        (SELECT COALESCE(AVG(max_mfe), 0) FROM signal_lab_v2_trades WHERE DATE(created_at) = target_date AND automation_source = 'FULL_AUTOMATION'),
        (SELECT COALESCE(MAX(max_mfe), 0) FROM signal_lab_v2_trades WHERE DATE(created_at) = target_date AND automation_source = 'FULL_AUTOMATION'),
        COUNT(CASE WHEN session = 'ASIA' THEN 1 END),
        COUNT(CASE WHEN session = 'LONDON' THEN 1 END),
        COUNT(CASE WHEN session = 'NY_AM' THEN 1 END),
        COUNT(CASE WHEN session = 'NY_LUNCH' THEN 1 END),
        COUNT(CASE WHEN session = 'NY_PM' THEN 1 END)
    FROM pending_signals 
    WHERE DATE(created_at) = target_date
    ON CONFLICT (date) DO UPDATE SET
        total_signals = EXCLUDED.total_signals,
        confirmed_signals = EXCLUDED.confirmed_signals,
        cancelled_signals = EXCLUDED.cancelled_signals,
        total_trades = EXCLUDED.total_trades,
        stopped_out_trades = EXCLUDED.stopped_out_trades,
        break_even_trades = EXCLUDED.break_even_trades,
        active_trades = EXCLUDED.active_trades,
        total_r_outcome = EXCLUDED.total_r_outcome,
        average_mfe = EXCLUDED.average_mfe,
        max_mfe_achieved = EXCLUDED.max_mfe_achieved,
        asia_signals = EXCLUDED.asia_signals,
        london_signals = EXCLUDED.london_signals,
        ny_am_signals = EXCLUDED.ny_am_signals,
        ny_lunch_signals = EXCLUDED.ny_lunch_signals,
        ny_pm_signals = EXCLUDED.ny_pm_signals,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update metrics
CREATE OR REPLACE FUNCTION trigger_update_metrics()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_automation_metrics();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic metrics updates
DROP TRIGGER IF EXISTS update_metrics_on_signal ON pending_signals;
CREATE TRIGGER update_metrics_on_signal
    AFTER INSERT OR UPDATE ON pending_signals
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_update_metrics();

DROP TRIGGER IF EXISTS update_metrics_on_trade ON signal_lab_v2_trades;
CREATE TRIGGER update_metrics_on_trade
    AFTER INSERT OR UPDATE ON signal_lab_v2_trades
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_update_metrics();

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;