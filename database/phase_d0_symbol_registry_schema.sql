-- Phase D.0: Symbol Registry
-- Purpose: Data-driven mapping for multi-symbol support

CREATE TABLE IF NOT EXISTS symbol_registry (
    internal_symbol TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    root TEXT NOT NULL,
    roll_rule TEXT NOT NULL CHECK (roll_rule IN ('c', 'n', 'v')),
    rank INTEGER NOT NULL DEFAULT 0,
    schema TEXT NOT NULL DEFAULT 'ohlcv-1m',
    stype_in TEXT NOT NULL DEFAULT 'continuous',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for active symbols
CREATE INDEX IF NOT EXISTS idx_symbol_registry_active ON symbol_registry(is_active) WHERE is_active = TRUE;

-- Index for dataset queries
CREATE INDEX IF NOT EXISTS idx_symbol_registry_dataset ON symbol_registry(dataset);

COMMENT ON TABLE symbol_registry IS 'Registry of tradeable symbols with Databento mapping configuration';
COMMENT ON COLUMN symbol_registry.internal_symbol IS 'Internal symbol format (e.g., GLBX.MDP3:NQ)';
COMMENT ON COLUMN symbol_registry.dataset IS 'Databento dataset (e.g., GLBX.MDP3)';
COMMENT ON COLUMN symbol_registry.root IS 'Instrument root (e.g., NQ)';
COMMENT ON COLUMN symbol_registry.roll_rule IS 'Databento roll rule: c=calendar, n=next, v=volume';
COMMENT ON COLUMN symbol_registry.rank IS 'Contract rank: 0=front month, 1=second month, etc.';
COMMENT ON COLUMN symbol_registry.schema IS 'Databento schema (default: ohlcv-1m)';
COMMENT ON COLUMN symbol_registry.stype_in IS 'Databento symbol type (default: continuous)';
COMMENT ON COLUMN symbol_registry.is_active IS 'Whether symbol is actively traded/monitored';

-- Insert default symbols
INSERT INTO symbol_registry (internal_symbol, dataset, root, roll_rule, rank, is_active)
VALUES 
    ('GLBX.MDP3:NQ', 'GLBX.MDP3', 'NQ', 'v', 0, TRUE),
    ('GLBX.MDP3:ES', 'GLBX.MDP3', 'ES', 'v', 0, TRUE),
    ('GLBX.MDP3:YM', 'GLBX.MDP3', 'YM', 'v', 0, TRUE),
    ('GLBX.MDP3:RTY', 'GLBX.MDP3', 'RTY', 'v', 0, TRUE)
ON CONFLICT (internal_symbol) DO NOTHING;
