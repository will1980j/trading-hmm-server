-- Phase C Corpus Schema
-- Idempotent, run-scoped, lockable historical signal corpus

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS signal_corpus_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL DEFAULT '1m',
    start_ts TIMESTAMPTZ NOT NULL,
    end_ts TIMESTAMPTZ NOT NULL,
    bars_table TEXT NOT NULL DEFAULT 'market_bars_ohlcv_1m_clean',
    bars_min_ts TIMESTAMPTZ NOT NULL,
    bars_max_ts TIMESTAMPTZ NOT NULL,
    bars_rowcount BIGINT NOT NULL,
    bars_fingerprint TEXT NOT NULL,
    logic_version TEXT NOT NULL,
    git_sha TEXT NOT NULL,
    config_fingerprint TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('RUNNING','COMPLETE','LOCKED','FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    locked_at TIMESTAMPTZ NULL,
    notes TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_corpus_runs_symbol_created
    ON signal_corpus_runs(symbol, created_at);
CREATE INDEX IF NOT EXISTS idx_corpus_runs_status
    ON signal_corpus_runs(status);

CREATE TABLE IF NOT EXISTS signal_corpus_batches (
    run_id UUID NOT NULL REFERENCES signal_corpus_runs(run_id) ON DELETE CASCADE,
    batch_start TIMESTAMPTZ NOT NULL,
    batch_end TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING','RUNNING','COMPLETE','FAILED')),
    bars_rowcount BIGINT NOT NULL DEFAULT 0,
    signals_emitted BIGINT NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NULL,
    finished_at TIMESTAMPTZ NULL,
    error TEXT NULL,
    PRIMARY KEY (run_id, batch_start, batch_end)
);

CREATE TABLE IF NOT EXISTS signal_corpus_triangles (
    run_id UUID NOT NULL REFERENCES signal_corpus_runs(run_id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('BULL','BEAR')),
    source_table TEXT NOT NULL DEFAULT 'market_bars_ohlcv_1m_clean',
    logic_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (run_id, symbol, ts, direction)
);

CREATE INDEX IF NOT EXISTS idx_corpus_triangles_run_ts
    ON signal_corpus_triangles(run_id, ts);

CREATE TABLE IF NOT EXISTS signal_corpus_snapshot (
    run_id UUID PRIMARY KEY REFERENCES signal_corpus_runs(run_id) ON DELETE CASCADE,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_triangles BIGINT NOT NULL,
    bull_count BIGINT NOT NULL,
    bear_count BIGINT NOT NULL,
    min_ts TIMESTAMPTZ NOT NULL,
    max_ts TIMESTAMPTZ NOT NULL,
    ym_counts_hash TEXT NOT NULL,
    direction_counts_hash TEXT NOT NULL,
    core_fingerprint_hash TEXT NOT NULL,
    integrity_failures BIGINT NOT NULL,
    notes TEXT NULL
);

CREATE OR REPLACE FUNCTION prevent_locked_corpus_modification()
RETURNS TRIGGER AS $$
DECLARE
    target_run_id UUID;
    run_status TEXT;
BEGIN
    target_run_id := COALESCE(NEW.run_id, OLD.run_id);
    
    SELECT status INTO run_status
    FROM signal_corpus_runs
    WHERE run_id = target_run_id;
    
    IF run_status = 'LOCKED' THEN
        RAISE EXCEPTION 'RUN_LOCKED: Cannot modify triangles for locked corpus run %', target_run_id;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_locked_corpus_modification ON signal_corpus_triangles;
CREATE TRIGGER trg_prevent_locked_corpus_modification
    BEFORE INSERT OR UPDATE OR DELETE ON signal_corpus_triangles
    FOR EACH ROW
    EXECUTE FUNCTION prevent_locked_corpus_modification();
