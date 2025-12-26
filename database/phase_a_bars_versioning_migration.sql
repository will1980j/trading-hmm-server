-- Phase A: Add dataset_version_id to market_bars_ohlcv_1m

ALTER TABLE market_bars_ohlcv_1m 
ADD COLUMN IF NOT EXISTS dataset_version_id TEXT;

CREATE INDEX IF NOT EXISTS idx_market_bars_version_symbol_ts 
ON market_bars_ohlcv_1m(dataset_version_id, symbol, ts);

COMMENT ON COLUMN market_bars_ohlcv_1m.dataset_version_id IS 
'Dataset version ID linking bars to immutable dataset version';
