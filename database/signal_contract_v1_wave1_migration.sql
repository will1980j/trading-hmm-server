-- Signal Contract V1 - Wave 1 Migration
-- Extends automated_signals table with timestamp semantics, signal candle, breakeven, and extremes fields

-- Patch 1: Timestamp Semantics (Foundation)
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS symbol TEXT;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS logic_version TEXT;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS status TEXT;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS signal_bar_open_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS signal_bar_close_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS confirmation_bar_open_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS confirmation_bar_close_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS entry_bar_open_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS entry_bar_close_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS exit_bar_open_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS exit_bar_close_ts TIMESTAMPTZ;

-- Patch 2: Signal Candle OHLC
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS signal_candle_high NUMERIC(12, 4);
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS signal_candle_low NUMERIC(12, 4);

-- Patch 4: Breakeven Fields
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS be_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS be_trigger_R NUMERIC(12, 4) DEFAULT 1.0;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS be_offset_points NUMERIC(12, 4) DEFAULT 0.0;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS be_triggered BOOLEAN DEFAULT FALSE;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS be_trigger_bar_open_ts TIMESTAMPTZ;
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS be_trigger_bar_close_ts TIMESTAMPTZ;

-- Patch 5: Extremes Storage
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS highest_high NUMERIC(12, 4);
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS lowest_low NUMERIC(12, 4);
ALTER TABLE automated_signals ADD COLUMN IF NOT EXISTS extremes_last_updated_bar_open_ts TIMESTAMPTZ;

-- Add indexes for new timestamp columns
CREATE INDEX IF NOT EXISTS idx_automated_signals_signal_bar_open ON automated_signals(signal_bar_open_ts);
CREATE INDEX IF NOT EXISTS idx_automated_signals_entry_bar_open ON automated_signals(entry_bar_open_ts);
CREATE INDEX IF NOT EXISTS idx_automated_signals_exit_bar_open ON automated_signals(exit_bar_open_ts);
CREATE INDEX IF NOT EXISTS idx_automated_signals_status ON automated_signals(status);
CREATE INDEX IF NOT EXISTS idx_automated_signals_symbol ON automated_signals(symbol);

-- Add comments
COMMENT ON COLUMN automated_signals.signal_bar_open_ts IS 'Bar OPEN time when triangle appeared (TradingView timestamp)';
COMMENT ON COLUMN automated_signals.signal_bar_close_ts IS 'Bar CLOSE time when triangle appeared (signal_bar_open_ts + 1 minute)';
COMMENT ON COLUMN automated_signals.confirmation_bar_open_ts IS 'Bar OPEN time of confirmation bar';
COMMENT ON COLUMN automated_signals.confirmation_bar_close_ts IS 'Bar CLOSE time of confirmation bar (when confirmation happened)';
COMMENT ON COLUMN automated_signals.entry_bar_open_ts IS 'Bar OPEN time when entry occurred (bar after confirmation)';
COMMENT ON COLUMN automated_signals.entry_bar_close_ts IS 'Bar CLOSE time of entry bar';
COMMENT ON COLUMN automated_signals.exit_bar_open_ts IS 'Bar OPEN time when exit occurred';
COMMENT ON COLUMN automated_signals.exit_bar_close_ts IS 'Bar CLOSE time when exit occurred';
COMMENT ON COLUMN automated_signals.signal_candle_high IS 'High of signal candle (for confirmation check)';
COMMENT ON COLUMN automated_signals.signal_candle_low IS 'Low of signal candle (for confirmation check)';
COMMENT ON COLUMN automated_signals.be_enabled IS 'Whether breakeven strategy is enabled';
COMMENT ON COLUMN automated_signals.be_trigger_R IS 'R-multiple for BE trigger (default 1.0)';
COMMENT ON COLUMN automated_signals.be_offset_points IS 'BE offset from entry price (default 0.0)';
COMMENT ON COLUMN automated_signals.be_triggered IS 'Whether BE was triggered';
COMMENT ON COLUMN automated_signals.be_trigger_bar_open_ts IS 'Bar OPEN time when BE triggered';
COMMENT ON COLUMN automated_signals.be_trigger_bar_close_ts IS 'Bar CLOSE time when BE triggered';
COMMENT ON COLUMN automated_signals.highest_high IS 'Highest high achieved (for bullish trades)';
COMMENT ON COLUMN automated_signals.lowest_low IS 'Lowest low achieved (for bearish trades)';
COMMENT ON COLUMN automated_signals.extremes_last_updated_bar_open_ts IS 'Last bar OPEN time when extremes were updated';
