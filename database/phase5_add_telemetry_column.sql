-- PHASE 5: Add telemetry column to automated_signals table
-- This migration adds JSONB column for full telemetry payload storage
-- Maintains backward compatibility with all existing columns

ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS telemetry JSONB;

-- Create index on telemetry for faster JSON queries
CREATE INDEX IF NOT EXISTS idx_automated_signals_telemetry 
ON automated_signals USING GIN (telemetry);

-- Create index on schema_version for telemetry detection
CREATE INDEX IF NOT EXISTS idx_automated_signals_telemetry_schema 
ON automated_signals ((telemetry->>'schema_version'));

-- Add comment
COMMENT ON COLUMN automated_signals.telemetry IS 'Full telemetry JSON payload from Phase 4+ indicators';
