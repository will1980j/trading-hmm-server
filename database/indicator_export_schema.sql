-- ============================================================================
-- INDICATOR EXPORT TABLES - Triangle-Canonical Trade Identity
-- ============================================================================
-- Two-layer architecture:
-- 1. Raw batches (immutable audit trail)
-- 2. Canonical ledgers (dashboard truth tables)

-- ============================================================================
-- TABLE A: indicator_export_batches (Raw Envelope Storage)
-- ============================================================================
-- Stores the raw batch envelope from TradingView
-- Immutable audit trail of "what TradingView actually said"

CREATE TABLE IF NOT EXISTS indicator_export_batches (
    id BIGSERIAL PRIMARY KEY,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL DEFAULT 'tradingview',
    event_type TEXT NOT NULL,  -- INDICATOR_EXPORT_V2, ALL_SIGNALS_EXPORT
    batch_number INTEGER NULL,
    batch_size INTEGER NULL,
    total_signals INTEGER NULL,
    payload_json JSONB NOT NULL,  -- Full request body
    payload_sha256 TEXT NOT NULL,  -- Deduplication hash
    is_valid BOOLEAN DEFAULT FALSE,
    validation_error TEXT NULL,
    UNIQUE(event_type, payload_sha256)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_export_batches_received_at ON indicator_export_batches(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_export_batches_event_type ON indicator_export_batches(event_type);
CREATE INDEX IF NOT EXISTS idx_export_batches_is_valid ON indicator_export_batches(is_valid);

-- ============================================================================
-- TABLE B: all_signals_ledger (Canonical All Signals Table)
-- ============================================================================
-- Triangle-keyed canonical truth table for "All Signals" tab
-- One row per triangle (pending, confirmed, cancelled)

CREATE TABLE IF NOT EXISTS all_signals_ledger (
    trade_id TEXT PRIMARY KEY,  -- Triangle-canonical ID
    triangle_time_ms BIGINT NOT NULL,
    confirmation_time_ms BIGINT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('Bullish', 'Bearish')),
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED')),
    bars_to_confirm INTEGER NULL,
    session TEXT NULL,
    entry_price NUMERIC(12, 4) NULL,
    stop_loss NUMERIC(12, 4) NULL,
    risk_points NUMERIC(12, 4) NULL,
    htf_daily TEXT NULL,
    htf_4h TEXT NULL,
    htf_1h TEXT NULL,
    htf_15m TEXT NULL,
    htf_5m TEXT NULL,
    htf_1m TEXT NULL,
    last_seen_batch_id BIGINT NULL REFERENCES indicator_export_batches(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_all_signals_triangle_time ON all_signals_ledger(triangle_time_ms DESC);
CREATE INDEX IF NOT EXISTS idx_all_signals_status ON all_signals_ledger(status);
CREATE INDEX IF NOT EXISTS idx_all_signals_direction ON all_signals_ledger(direction);
CREATE INDEX IF NOT EXISTS idx_all_signals_updated_at ON all_signals_ledger(updated_at DESC);

-- ============================================================================
-- TABLE C: confirmed_signals_ledger (Canonical Confirmed Signals Table)
-- ============================================================================
-- Triangle-keyed canonical truth table for "Confirmed Signals" tab
-- One row per confirmed signal with MFE/MAE tracking

CREATE TABLE IF NOT EXISTS confirmed_signals_ledger (
    trade_id TEXT PRIMARY KEY,  -- Triangle-canonical ID
    triangle_time_ms BIGINT NOT NULL,
    confirmation_time_ms BIGINT NULL,
    date DATE NULL,
    session TEXT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('Bullish', 'Bearish')),
    entry NUMERIC(12, 4) NULL,
    stop NUMERIC(12, 4) NULL,
    be_mfe NUMERIC(12, 6) NULL,
    no_be_mfe NUMERIC(12, 6) NULL,
    mae NUMERIC(12, 6) NULL,
    completed BOOLEAN NULL,
    last_seen_batch_id BIGINT NULL REFERENCES indicator_export_batches(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_confirmed_signals_date ON confirmed_signals_ledger(date DESC);
CREATE INDEX IF NOT EXISTS idx_confirmed_signals_session ON confirmed_signals_ledger(session);
CREATE INDEX IF NOT EXISTS idx_confirmed_signals_completed ON confirmed_signals_ledger(completed);
CREATE INDEX IF NOT EXISTS idx_confirmed_signals_triangle_time ON confirmed_signals_ledger(triangle_time_ms DESC);
CREATE INDEX IF NOT EXISTS idx_confirmed_signals_updated_at ON confirmed_signals_ledger(updated_at DESC);

-- ============================================================================
-- VERIFICATION QUERIES (Run separately after migration)
-- ============================================================================

-- Commented out to prevent auto-execution during schema application
-- Run these manually to verify migration success:

/*
-- Check tables were created
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_name IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger')
ORDER BY table_name;

-- Check indexes were created
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger')
ORDER BY tablename, indexname;
*/
