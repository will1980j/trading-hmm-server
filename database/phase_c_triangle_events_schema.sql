-- Phase C Stage 1: Triangle Events Table
-- Stores historical triangle signals generated from Databento OHLCV data

CREATE TABLE IF NOT EXISTS triangle_events_v1 (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('BULL', 'BEAR')),
    bias_1m TEXT NOT NULL,
    bias_m5 TEXT NOT NULL,
    bias_m15 TEXT NOT NULL,
    bias_h1 TEXT NOT NULL,
    bias_h4 TEXT NOT NULL,
    bias_d1 TEXT NOT NULL,
    htf_bullish BOOLEAN NOT NULL,
    htf_bearish BOOLEAN NOT NULL,
    require_engulfing BOOLEAN NOT NULL,
    require_sweep_engulfing BOOLEAN NOT NULL,
    htf_aligned_only BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(symbol, ts, direction)
);

CREATE INDEX IF NOT EXISTS idx_triangle_events_symbol_ts 
ON triangle_events_v1(symbol, ts DESC);

CREATE INDEX IF NOT EXISTS idx_triangle_events_direction 
ON triangle_events_v1(direction);

CREATE INDEX IF NOT EXISTS idx_triangle_events_created_at 
ON triangle_events_v1(created_at DESC);

COMMENT ON TABLE triangle_events_v1 IS 
'Historical triangle signals generated from Databento OHLCV using Phase B parity modules';

COMMENT ON COLUMN triangle_events_v1.direction IS 
'BULL or BEAR triangle signal';

COMMENT ON COLUMN triangle_events_v1.ts IS 
'Bar timestamp (UTC) when triangle appeared';
