-- Phase C: Clean OHLCV Overlay Table
-- Purpose: Store validated, clean OHLCV bars for TradingView-visible range
-- Source: Re-ingested from Databento with strict validation

CREATE TABLE IF NOT EXISTS market_bars_ohlcv_1m_clean (
    ts TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    volume BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (symbol, ts)
);

-- Index for time-range queries
CREATE INDEX IF NOT EXISTS idx_clean_ohlcv_symbol_ts ON market_bars_ohlcv_1m_clean(symbol, ts);

-- Index for timestamp queries
CREATE INDEX IF NOT EXISTS idx_clean_ohlcv_ts ON market_bars_ohlcv_1m_clean(ts);

COMMENT ON TABLE market_bars_ohlcv_1m_clean IS 'Clean, validated OHLCV bars re-ingested from Databento for Phase C parity testing';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.ts IS 'Bar close timestamp (UTC)';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.symbol IS 'Databento symbol (e.g., GLBX.MDP3:NQ)';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.open IS 'Open price';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.high IS 'High price';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.low IS 'Low price';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.close IS 'Close price';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.volume IS 'Volume (if available)';
COMMENT ON COLUMN market_bars_ohlcv_1m_clean.created_at IS 'Timestamp when row was inserted';
