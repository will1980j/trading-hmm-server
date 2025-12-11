-- ============================================================================
-- HYBRID SIGNAL SYNCHRONIZATION SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Purpose: Enhance automated_signals table for enterprise-grade data integrity
-- Version: 1.0.0
-- Date: 2025-12-12
-- ============================================================================

-- ============================================================================
-- PART 1: ADD NEW COLUMNS TO automated_signals TABLE
-- ============================================================================

-- Data Source Tracking
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS data_source VARCHAR(50) DEFAULT 'indicator_realtime'
CHECK (data_source IN ('indicator_realtime', 'indicator_polling', 'backend_calculated', 'reconciled'));

-- Confidence and Quality Metrics
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS confidence_score DECIMAL(3,2) DEFAULT 1.0
CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0);

-- Reconciliation Tracking
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS reconciliation_timestamp TIMESTAMP;

ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS reconciliation_reason TEXT;

-- Data Integrity
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS payload_checksum VARCHAR(64);

ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS sequence_number BIGINT;

-- Confirmation Tracking
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS confirmation_time TIMESTAMP;

ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS bars_to_confirmation INTEGER;

-- Extended Targets (up to 20R)
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS targets_extended JSONB;

-- HTF Alignment Data
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS htf_alignment JSONB;

-- Full Payload Storage (if not already exists)
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS raw_payload JSONB;

-- ============================================================================
-- PART 2: CREATE SIGNAL HEALTH METRICS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS signal_health_metrics (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT NOW(),
    health_score INTEGER NOT NULL DEFAULT 100 CHECK (health_score >= 0 AND health_score <= 100),
    gap_flags JSONB NOT NULL DEFAULT '{}',
    last_check TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Note: No foreign key because trade_id is not unique in automated_signals
    -- (multiple events per trade_id)
    
    -- Unique constraint (one health record per signal)
    CONSTRAINT unique_signal_health UNIQUE (trade_id)
);

-- Gap flags structure (stored as JSONB):
-- {
--   "no_mfe_update": false,
--   "no_entry_price": false,
--   "no_stop_loss": false,
--   "no_mae": false,
--   "no_session": false,
--   "no_signal_date": false,
--   "last_mfe_update": "2025-12-12T10:30:00",
--   "gap_count": 0
-- }

-- ============================================================================
-- PART 3: CREATE SYNC AUDIT LOG TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_audit_log (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    data_source VARCHAR(50) NOT NULL,
    fields_filled JSONB,
    confidence_score DECIMAL(3,2),
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Action types: 'gap_detected', 'gap_filled', 'polling_request', 'polling_response', 
--                'reconciliation_attempted', 'reconciliation_success', 'reconciliation_failed'

-- ============================================================================
-- PART 4: CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Indexes on automated_signals new columns
CREATE INDEX IF NOT EXISTS idx_automated_signals_data_source 
    ON automated_signals(data_source);

CREATE INDEX IF NOT EXISTS idx_automated_signals_confidence 
    ON automated_signals(confidence_score);

CREATE INDEX IF NOT EXISTS idx_automated_signals_sequence 
    ON automated_signals(trade_id, sequence_number);

CREATE INDEX IF NOT EXISTS idx_automated_signals_reconciliation 
    ON automated_signals(reconciliation_timestamp) 
    WHERE reconciliation_timestamp IS NOT NULL;

-- Indexes on signal_health_metrics
CREATE INDEX IF NOT EXISTS idx_signal_health_last_update 
    ON signal_health_metrics(last_update);

CREATE INDEX IF NOT EXISTS idx_signal_health_score 
    ON signal_health_metrics(health_score);

CREATE INDEX IF NOT EXISTS idx_signal_health_gaps 
    ON signal_health_metrics USING GIN (gap_flags);

-- Indexes on sync_audit_log
CREATE INDEX IF NOT EXISTS idx_sync_audit_trade_id 
    ON sync_audit_log(trade_id);

CREATE INDEX IF NOT EXISTS idx_sync_audit_timestamp 
    ON sync_audit_log(action_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sync_audit_action_type 
    ON sync_audit_log(action_type);

-- ============================================================================
-- PART 5: CREATE HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate health score based on gap flags
CREATE OR REPLACE FUNCTION calculate_signal_health_score(gaps JSONB)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 100;
    gap_count INTEGER := 0;
BEGIN
    -- Count gaps
    IF (gaps->>'no_mfe_update')::boolean THEN gap_count := gap_count + 1; END IF;
    IF (gaps->>'no_entry_price')::boolean THEN gap_count := gap_count + 1; END IF;
    IF (gaps->>'no_stop_loss')::boolean THEN gap_count := gap_count + 1; END IF;
    IF (gaps->>'no_mae')::boolean THEN gap_count := gap_count + 1; END IF;
    IF (gaps->>'no_session')::boolean THEN gap_count := gap_count + 1; END IF;
    IF (gaps->>'no_signal_date')::boolean THEN gap_count := gap_count + 1; END IF;
    
    -- Deduct points per gap (16.67 points per gap, 6 gaps = 0 score)
    score := score - (gap_count * 17);
    
    -- Ensure score stays in valid range
    IF score < 0 THEN score := 0; END IF;
    
    RETURN score;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to update signal health metrics
CREATE OR REPLACE FUNCTION update_signal_health(p_trade_id VARCHAR(100))
RETURNS VOID AS $$
DECLARE
    v_gaps JSONB := '{}';
    v_health_score INTEGER;
    v_last_mfe_update TIMESTAMP;
BEGIN
    -- Check for gaps
    SELECT 
        MAX(timestamp) FILTER (WHERE event_type = 'MFE_UPDATE')
    INTO v_last_mfe_update
    FROM automated_signals
    WHERE trade_id = p_trade_id;
    
    -- Build gap flags
    v_gaps := jsonb_build_object(
        'no_mfe_update', (v_last_mfe_update IS NULL OR v_last_mfe_update < NOW() - INTERVAL '2 minutes'),
        'no_entry_price', EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND entry_price IS NULL),
        'no_stop_loss', EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND stop_loss IS NULL),
        'no_mae', NOT EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND mae_global_r IS NOT NULL AND mae_global_r != 0),
        'no_session', EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND session IS NULL),
        'no_signal_date', EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND signal_date IS NULL),
        'last_mfe_update', v_last_mfe_update,
        'gap_count', (
            CASE WHEN v_last_mfe_update IS NULL OR v_last_mfe_update < NOW() - INTERVAL '2 minutes' THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND entry_price IS NULL) THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND stop_loss IS NULL) THEN 1 ELSE 0 END +
            CASE WHEN NOT EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND mae_global_r IS NOT NULL AND mae_global_r != 0) THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND session IS NULL) THEN 1 ELSE 0 END +
            CASE WHEN EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = p_trade_id AND event_type = 'ENTRY' AND signal_date IS NULL) THEN 1 ELSE 0 END
        )
    );
    
    -- Calculate health score
    v_health_score := calculate_signal_health_score(v_gaps);
    
    -- Insert or update health metrics
    INSERT INTO signal_health_metrics (trade_id, last_update, health_score, gap_flags, last_check)
    VALUES (p_trade_id, NOW(), v_health_score, v_gaps, NOW())
    ON CONFLICT (trade_id) 
    DO UPDATE SET
        last_update = NOW(),
        health_score = v_health_score,
        gap_flags = v_gaps,
        last_check = NOW(),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PART 6: CREATE VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Signals with health metrics
CREATE OR REPLACE VIEW signals_with_health AS
SELECT 
    s.*,
    h.health_score,
    h.gap_flags,
    h.last_check
FROM automated_signals s
LEFT JOIN signal_health_metrics h ON s.trade_id = h.trade_id
WHERE s.event_type = 'ENTRY';

-- View: Signals with gaps (health score < 100)
CREATE OR REPLACE VIEW signals_with_gaps AS
SELECT 
    trade_id,
    health_score,
    gap_flags,
    last_update
FROM signal_health_metrics
WHERE health_score < 100
ORDER BY health_score ASC, last_update DESC;

-- ============================================================================
-- PART 7: ROLLBACK SCRIPT (IF NEEDED)
-- ============================================================================

-- To rollback this migration, run:
-- DROP VIEW IF EXISTS signals_with_gaps;
-- DROP VIEW IF EXISTS signals_with_health;
-- DROP FUNCTION IF EXISTS update_signal_health(VARCHAR);
-- DROP FUNCTION IF EXISTS calculate_signal_health_score(JSONB);
-- DROP TABLE IF EXISTS sync_audit_log;
-- DROP TABLE IF EXISTS signal_health_metrics;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS data_source;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS confidence_score;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS reconciliation_timestamp;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS reconciliation_reason;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS payload_checksum;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS sequence_number;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS confirmation_time;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS bars_to_confirmation;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS targets_extended;
-- ALTER TABLE automated_signals DROP COLUMN IF EXISTS htf_alignment;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check new columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'automated_signals'
AND column_name IN ('data_source', 'confidence_score', 'reconciliation_timestamp', 
                    'payload_checksum', 'sequence_number', 'confirmation_time',
                    'bars_to_confirmation', 'targets_extended', 'htf_alignment')
ORDER BY column_name;

-- Check new tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('signal_health_metrics', 'sync_audit_log');

-- Check indexes created
SELECT indexname, tablename 
FROM pg_indexes 
WHERE tablename IN ('automated_signals', 'signal_health_metrics', 'sync_audit_log')
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Test health score calculation
SELECT calculate_signal_health_score('{"no_mfe_update": true, "no_mae": true}'::jsonb) as test_score;
-- Expected: 66 (100 - 17*2)

-- ============================================================================
-- END OF SCHEMA MIGRATION
-- ============================================================================
