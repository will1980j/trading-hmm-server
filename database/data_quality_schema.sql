-- Data Quality System Database Schema
-- Phase 1: Database Tables for Reconciliation, Conflicts, and Metrics

-- Table 1: Reconciliation Records
CREATE TABLE IF NOT EXISTS data_quality_reconciliations (
    id SERIAL PRIMARY KEY,
    reconciliation_date DATE NOT NULL,
    reconciliation_time TIMESTAMP NOT NULL,
    signals_in_indicator INTEGER NOT NULL,
    signals_in_database INTEGER NOT NULL,
    missing_signals INTEGER DEFAULT 0,
    incomplete_signals INTEGER DEFAULT 0,
    mfe_mismatches INTEGER DEFAULT 0,
    conflicts_requiring_review INTEGER DEFAULT 0,
    auto_resolved INTEGER DEFAULT 0,
    webhook_success_rate DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'complete',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for date queries
CREATE INDEX IF NOT EXISTS idx_reconciliations_date ON data_quality_reconciliations(reconciliation_date DESC);

-- Table 2: Data Conflicts
CREATE TABLE IF NOT EXISTS data_quality_conflicts (
    id SERIAL PRIMARY KEY,
    reconciliation_id INTEGER REFERENCES data_quality_reconciliations(id) ON DELETE CASCADE,
    trade_id VARCHAR(50) NOT NULL,
    conflict_type VARCHAR(50) NOT NULL,
    webhook_value TEXT,
    indicator_value TEXT,
    field_name VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    resolution VARCHAR(20),
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for conflict queries
CREATE INDEX IF NOT EXISTS idx_conflicts_status ON data_quality_conflicts(status);
CREATE INDEX IF NOT EXISTS idx_conflicts_trade_id ON data_quality_conflicts(trade_id);
CREATE INDEX IF NOT EXISTS idx_conflicts_reconciliation ON data_quality_conflicts(reconciliation_id);

-- Table 3: Daily Quality Metrics
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL UNIQUE,
    webhook_success_rate DECIMAL(5,2),
    signals_captured INTEGER,
    signals_missed INTEGER,
    avg_reconciliation_time INTEGER,
    system_health VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for date range queries
CREATE INDEX IF NOT EXISTS idx_metrics_date ON data_quality_metrics(metric_date DESC);

-- Comments for documentation
COMMENT ON TABLE data_quality_reconciliations IS 'Daily reconciliation records comparing indicator vs database';
COMMENT ON TABLE data_quality_conflicts IS 'Data discrepancies requiring review or auto-resolution';
COMMENT ON TABLE data_quality_metrics IS 'Daily aggregated quality metrics for trending';

COMMENT ON COLUMN data_quality_conflicts.conflict_type IS 'Types: missing_signal, missing_field, mfe_mismatch, timestamp_mismatch, direction_mismatch';
COMMENT ON COLUMN data_quality_conflicts.severity IS 'Severity: low, medium, high, critical';
COMMENT ON COLUMN data_quality_conflicts.status IS 'Status: pending, resolved, ignored';
COMMENT ON COLUMN data_quality_conflicts.resolution IS 'Resolution: trust_indicator, trust_webhook, manual, auto_filled';
