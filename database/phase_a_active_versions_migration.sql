-- Phase A: Active dataset versions (zero-row update solution)

CREATE TABLE IF NOT EXISTS active_dataset_versions (
    symbol TEXT PRIMARY KEY,
    dataset_version_id TEXT NOT NULL,
    set_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_active_dataset_versions_version
ON active_dataset_versions(dataset_version_id);

-- Seed NQ and MNQ mappings
INSERT INTO active_dataset_versions (symbol, dataset_version_id)
VALUES 
    ('GLBX.MDP3:NQ', 'd4f77fc8f829782b'),
    ('GLBX.MDP3:MNQ', 'a5f8315acbaed9a1')
ON CONFLICT (symbol) DO NOTHING;

COMMENT ON TABLE active_dataset_versions IS 
'Maps symbols to their active dataset version (avoids mass-updating bars table)';
