-- ============================================================================
-- AUTOMATED SIGNALS TABLE - Add to Railway Database
-- ============================================================================
-- Run this SQL directly in Railway's PostgreSQL console
-- This is the DEFINITIVE schema - no more guessing

-- Drop existing table if you want to start fresh (CAREFUL!)
-- DROP TABLE IF EXISTS automated_signals CASCADE;

-- Create the table
CREATE TABLE IF NOT EXISTS automated_signals (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(20) NOT NULL,
    trade_id VARCHAR(100) NOT NULL,
    direction VARCHAR(10),
    entry_price DECIMAL(10, 2),
    stop_loss DECIMAL(10, 2),
    risk_distance DECIMAL(10, 2),
    target_1r DECIMAL(10, 2),
    target_2r DECIMAL(10, 2),
    target_3r DECIMAL(10, 2),
    target_5r DECIMAL(10, 2),
    target_10r DECIMAL(10, 2),
    target_20r DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    mfe DECIMAL(10, 4),
    exit_price DECIMAL(10, 2),
    final_mfe DECIMAL(10, 4),
    session VARCHAR(20),
    bias VARCHAR(20),
    account_size DECIMAL(15, 2),
    risk_percent DECIMAL(5, 2),
    contracts INTEGER,
    risk_amount DECIMAL(10, 2),
    timestamp BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_automated_signals_trade_id ON automated_signals(trade_id);
CREATE INDEX IF NOT EXISTS idx_automated_signals_event_type ON automated_signals(event_type);
CREATE INDEX IF NOT EXISTS idx_automated_signals_timestamp ON automated_signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_automated_signals_created_at ON automated_signals(created_at DESC);

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON automated_signals TO your_user;
-- GRANT USAGE, SELECT ON SEQUENCE automated_signals_id_seq TO your_user;

-- Verify table was created
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'automated_signals'
ORDER BY ordinal_position;

-- Test insert (optional - remove after testing)
-- INSERT INTO automated_signals (event_type, trade_id, direction, entry_price, stop_loss, session, bias, timestamp)
-- VALUES ('ENTRY', 'TEST_001', 'LONG', 21250.50, 21225.50, 'NY AM', 'Bullish', 1699999999999);

-- Verify insert worked
-- SELECT * FROM automated_signals WHERE trade_id = 'TEST_001';
