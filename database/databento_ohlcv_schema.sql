-- ============================================================================
-- DATABENTO OHLCV-1M INGESTION SCHEMA
-- ============================================================================

CREATE TABLE IF NOT EXISTS market_bars_ohlcv_1m (
    vendor TEXT NOT NULL DEFAULT 'databento',
    schema TEXT NOT NULL DEFAULT 'ohlcv-1m',
    symbol TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    ts_ms BIGINT NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NULL,
    ingestion_run_id BIGINT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (symbol, ts),
    CONSTRAINT chk_ohlc_valid CHECK (
        high >= open AND high >= close AND high >= low AND
        low <= open AND low <= close
    )
);

CREATE INDEX IF NOT EXISTS idx_market_bars_ts_desc ON market_bars_ohlcv_1m (ts DESC);
CREATE INDEX IF NOT EXISTS idx_market_bars_symbol_ts ON market_bars_ohlcv_1m (symbol, ts DESC);
CREATE INDEX IF NOT EXISTS idx_market_bars_ingestion_run ON market_bars_ohlcv_1m (ingestion_run_id);

CREATE TABLE IF NOT EXISTS data_ingest_runs (
    id BIGSERIAL PRIMARY KEY,
    vendor TEXT NOT NULL,
    dataset TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_sha256 TEXT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ NULL,
    row_count BIGINT NOT NULL DEFAULT 0,
    inserted_count BIGINT NOT NULL DEFAULT 0,
    updated_count BIGINT NOT NULL DEFAULT 0,
    min_ts TIMESTAMPTZ NULL,
    max_ts TIMESTAMPTZ NULL,
    status TEXT NOT NULL DEFAULT 'running',
    error TEXT NULL,
    CONSTRAINT chk_status_valid CHECK (status IN ('running', 'success', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_ingest_runs_started ON data_ingest_runs (started_at DESC);
CREATE INDEX IF NOT EXISTS idx_ingest_runs_dataset ON data_ingest_runs (dataset, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_ingest_runs_status ON data_ingest_runs (status);
