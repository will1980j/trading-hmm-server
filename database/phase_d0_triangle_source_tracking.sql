-- Phase D.0: Add source tracking to triangle_events_v1
-- Purpose: Track which OHLCV table and logic version generated each triangle

-- Add source_table column
ALTER TABLE triangle_events_v1 
ADD COLUMN IF NOT EXISTS source_table TEXT;

-- Add logic_version column
ALTER TABLE triangle_events_v1 
ADD COLUMN IF NOT EXISTS logic_version TEXT;

-- Add index for source_table queries
CREATE INDEX IF NOT EXISTS idx_triangle_events_source_table 
ON triangle_events_v1(source_table);

-- Add comments
COMMENT ON COLUMN triangle_events_v1.source_table IS 
'Source OHLCV table: market_bars_ohlcv_1m_clean (preferred) or market_bars_ohlcv_1m (legacy)';

COMMENT ON COLUMN triangle_events_v1.logic_version IS 
'Git hash or version string of signal generation logic used';
