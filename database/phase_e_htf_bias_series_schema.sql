-- Phase E: HTF Bias Series
-- Purpose: Persist queryable HTF bias timeline for strategy analysis

CREATE TABLE IF NOT EXISTS bias_series_1m_v1 (
    symbol TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    bias_1m TEXT NOT NULL,
    bias_5m TEXT NOT NULL,
    bias_15m TEXT NOT NULL,
    bias_1h TEXT NOT NULL,
    bias_4h TEXT NOT NULL,
    bias_1d TEXT NOT NULL,
    source_table TEXT NOT NULL,
    logic_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (symbol, ts)
);

-- Index for time-range queries
CREATE INDEX IF NOT EXISTS idx_bias_series_symbol_ts ON bias_series_1m_v1(symbol, ts DESC);

-- Index for source tracking
CREATE INDEX IF NOT EXISTS idx_bias_series_source ON bias_series_1m_v1(source_table);

COMMENT ON TABLE bias_series_1m_v1 IS 'HTF bias timeline at 1m resolution with forward-fill semantics';
COMMENT ON COLUMN bias_series_1m_v1.ts IS '1m bar OPEN timestamp (UTC) - matches TradingView';
COMMENT ON COLUMN bias_series_1m_v1.bias_1m IS '1-minute bias (Bullish/Bearish/Neutral)';
COMMENT ON COLUMN bias_series_1m_v1.bias_5m IS '5-minute bias (forward-filled)';
COMMENT ON COLUMN bias_series_1m_v1.bias_15m IS '15-minute bias (forward-filled)';
COMMENT ON COLUMN bias_series_1m_v1.bias_1h IS '1-hour bias (forward-filled)';
COMMENT ON COLUMN bias_series_1m_v1.bias_4h IS '4-hour bias (forward-filled)';
COMMENT ON COLUMN bias_series_1m_v1.bias_1d IS 'Daily bias (forward-filled)';
COMMENT ON COLUMN bias_series_1m_v1.source_table IS 'Source OHLCV table (should be market_bars_ohlcv_1m_clean)';
COMMENT ON COLUMN bias_series_1m_v1.logic_version IS 'Git hash or version of bias calculation logic';
