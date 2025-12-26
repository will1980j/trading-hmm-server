-- Phase A: Add dataset_version_id to data_ingest_runs

ALTER TABLE data_ingest_runs 
ADD COLUMN IF NOT EXISTS dataset_version_id TEXT;

CREATE INDEX IF NOT EXISTS idx_ingest_runs_version 
ON data_ingest_runs(dataset_version_id);

COMMENT ON COLUMN data_ingest_runs.dataset_version_id IS 
'Immutable dataset version ID: sha256(vendor|dataset|file_sha256)[:16]';
