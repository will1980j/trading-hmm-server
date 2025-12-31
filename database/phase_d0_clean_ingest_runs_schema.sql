-- Phase D.0: Clean Ingest Runs Log
-- Purpose: Track all clean OHLCV re-ingestion operations

CREATE TABLE IF NOT EXISTS clean_ingest_runs (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    start_ts TIMESTAMPTZ NOT NULL,
    end_ts TIMESTAMPTZ NOT NULL,
    bars_received INTEGER NOT NULL,
    bars_inserted INTEGER NOT NULL,
    bars_updated INTEGER NOT NULL,
    bars_skipped INTEGER NOT NULL,
    batch_commits INTEGER NOT NULL DEFAULT 0,
    retries INTEGER NOT NULL DEFAULT 0,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_seconds NUMERIC(10, 2),
    status TEXT NOT NULL DEFAULT 'success' CHECK (status IN ('success', 'failed', 'partial')),
    error TEXT
);

-- Index for symbol queries
CREATE INDEX IF NOT EXISTS idx_clean_ingest_symbol ON clean_ingest_runs(symbol, run_at DESC);

-- Index for time range queries
CREATE INDEX IF NOT EXISTS idx_clean_ingest_time_range ON clean_ingest_runs(start_ts, end_ts);

-- Index for status queries
CREATE INDEX IF NOT EXISTS idx_clean_ingest_status ON clean_ingest_runs(status);

COMMENT ON TABLE clean_ingest_runs IS 'Audit log for clean OHLCV re-ingestion operations';
COMMENT ON COLUMN clean_ingest_runs.symbol IS 'Internal symbol format (e.g., GLBX.MDP3:NQ)';
COMMENT ON COLUMN clean_ingest_runs.start_ts IS 'Start of ingestion time range (UTC)';
COMMENT ON COLUMN clean_ingest_runs.end_ts IS 'End of ingestion time range (UTC)';
COMMENT ON COLUMN clean_ingest_runs.bars_received IS 'Total bars received from Databento';
COMMENT ON COLUMN clean_ingest_runs.bars_inserted IS 'New bars inserted';
COMMENT ON COLUMN clean_ingest_runs.bars_updated IS 'Existing bars updated';
COMMENT ON COLUMN clean_ingest_runs.bars_skipped IS 'Invalid bars skipped';
COMMENT ON COLUMN clean_ingest_runs.batch_commits IS 'Number of batch commits executed';
COMMENT ON COLUMN clean_ingest_runs.retries IS 'Number of reconnection retries';
COMMENT ON COLUMN clean_ingest_runs.duration_seconds IS 'Total ingestion duration';
COMMENT ON COLUMN clean_ingest_runs.status IS 'success, failed, or partial';
