
-- Complete Automation Database Schema for Data Collection & Forward Testing

-- Enhanced signals V2 table (if not exists)
CREATE TABLE IF NOT EXISTS enhanced_signals_v2 (
    id SERIAL PRIMARY KEY,
    trade_uuid UUID DEFAULT gen_random_uuid(),
    signal_type VARCHAR(10) NOT NULL,
    session VARCHAR(20) NOT NULL,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
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
    
    -- Trade Execution Data
    entry_price DECIMAL(10,2),
    entry_timestamp BIGINT,
    stop_loss_price DECIMAL(10,2),
    stop_loss_scenario VARCHAR(50),
    stop_loss_reasoning TEXT,
    
    -- R-Multiple Targets
    target_1r DECIMAL(10,2),
    target_2r DECIMAL(10,2),
    target_3r DECIMAL(10,2),
    target_5r DECIMAL(10,2),
    target_10r DECIMAL(10,2),
    target_20r DECIMAL(10,2),
    risk_distance DECIMAL(10,2),
    
    -- MFE Tracking for Forward Testing
    current_mfe DECIMAL(10,4) DEFAULT 0,
    max_mfe DECIMAL(10,4) DEFAULT 0,
    mfe_tracking_active BOOLEAN DEFAULT FALSE,
    last_mfe_update TIMESTAMP WITH TIME ZONE,
    
    -- Status Tracking
    status VARCHAR(30) DEFAULT 'awaiting_confirmation',
    automation_level VARCHAR(30) DEFAULT 'basic',
    resolved BOOLEAN DEFAULT FALSE,
    resolution_type VARCHAR(20),
    resolution_price DECIMAL(10,2),
    resolution_timestamp BIGINT,
    final_mfe DECIMAL(10,4),
    
    -- Data Collection & Forward Testing
    data_collection_mode BOOLEAN DEFAULT TRUE,
    forward_testing BOOLEAN DEFAULT TRUE,
    prop_firm_ready BOOLEAN DEFAULT FALSE,
    
    -- Data Storage
    market_context JSONB,
    raw_signal_data JSONB,
    
    -- Constraints
    CONSTRAINT valid_signal_type CHECK (signal_type IN ('Bullish', 'Bearish')),
    CONSTRAINT valid_status CHECK (status IN ('awaiting_confirmation', 'confirmed', 'active', 'resolved', 'cancelled'))
);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_automation_level ON enhanced_signals_v2(automation_level);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_data_collection ON enhanced_signals_v2(data_collection_mode);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_forward_testing ON enhanced_signals_v2(forward_testing);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_session_type ON enhanced_signals_v2(session, signal_type);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_created_at ON enhanced_signals_v2(created_at DESC);

-- Add automation-specific columns to existing table if they don't exist
DO $$ 
BEGIN
    -- Add automation level if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'automation_level') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN automation_level VARCHAR(30) DEFAULT 'basic';
    END IF;
    
    -- Add data collection mode if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'data_collection_mode') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN data_collection_mode BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Add forward testing flag if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'forward_testing') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN forward_testing BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Add prop firm readiness if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'prop_firm_ready') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN prop_firm_ready BOOLEAN DEFAULT FALSE;
    END IF;
END $$;
