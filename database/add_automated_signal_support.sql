-- Migration: Add Automated Signal Support to Signal Lab V2
-- This adds the necessary fields to support automated signals from TradingView webhooks

-- Add new columns to existing signal_lab_trades table
ALTER TABLE signal_lab_trades 
ADD COLUMN IF NOT EXISTS signal_id VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'manual' CHECK (source IN ('manual', 'automated')),
ADD COLUMN IF NOT EXISTS entry_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS sl_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS risk_distance DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS be_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS target_1r DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS target_2r DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS target_3r DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS lowest_low DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS highest_high DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed')),
ADD COLUMN IF NOT EXISTS completion_reason VARCHAR(50);

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_signal_lab_signal_id ON signal_lab_trades(signal_id);
CREATE INDEX IF NOT EXISTS idx_signal_lab_source ON signal_lab_trades(source);
CREATE INDEX IF NOT EXISTS idx_signal_lab_status ON signal_lab_trades(status);

-- Update existing manual entries to have source = 'manual'
UPDATE signal_lab_trades SET source = 'manual' WHERE source IS NULL;

-- Add comment to table
COMMENT ON TABLE signal_lab_trades IS 'Unified signal lab table supporting both manual and automated signal entry';
COMMENT ON COLUMN signal_lab_trades.signal_id IS 'Unique identifier for automated signals (format: YYYYMMDD_HHMMSS_BIAS)';
COMMENT ON COLUMN signal_lab_trades.source IS 'Source of signal: manual (entered via UI) or automated (from TradingView webhook)';
COMMENT ON COLUMN signal_lab_trades.entry_price IS 'Entry price for the trade';
COMMENT ON COLUMN signal_lab_trades.sl_price IS 'Stop loss price';
COMMENT ON COLUMN signal_lab_trades.risk_distance IS 'Distance from entry to stop loss';
COMMENT ON COLUMN signal_lab_trades.be_price IS 'Break-even price (usually same as entry_price)';
COMMENT ON COLUMN signal_lab_trades.target_1r IS '1R target price';
COMMENT ON COLUMN signal_lab_trades.target_2r IS '2R target price';
COMMENT ON COLUMN signal_lab_trades.target_3r IS '3R target price';
COMMENT ON COLUMN signal_lab_trades.lowest_low IS 'Lowest low reached since signal creation (for bullish signals)';
COMMENT ON COLUMN signal_lab_trades.highest_high IS 'Highest high reached since signal creation (for bearish signals)';
COMMENT ON COLUMN signal_lab_trades.status IS 'Signal status: active (still running) or completed (stopped out)';
COMMENT ON COLUMN signal_lab_trades.completion_reason IS 'Reason for completion: stop_loss_hit, target_hit, etc.';
