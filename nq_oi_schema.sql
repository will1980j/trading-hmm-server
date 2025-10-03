-- NQ Options Open Interest Database Schema

-- Raw QuikStrike snapshots
CREATE TABLE IF NOT EXISTS raw_quikstrike_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_url TEXT NOT NULL,
    instrument TEXT NOT NULL,
    payload JSONB NOT NULL,
    hash TEXT NOT NULL,
    UNIQUE(hash, instrument, scraped_at::date)
);

-- Individual strike level OI data
CREATE TABLE IF NOT EXISTS oi_strikes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    instrument TEXT NOT NULL,
    expiry_date DATE NOT NULL,
    dte INTEGER NOT NULL,
    strike NUMERIC NOT NULL,
    call_oi INTEGER NOT NULL DEFAULT 0,
    put_oi INTEGER NOT NULL DEFAULT 0,
    total_oi INTEGER NOT NULL DEFAULT 0,
    call_oi_change INTEGER NULL,
    put_oi_change INTEGER NULL,
    volume_call INTEGER NULL,
    volume_put INTEGER NULL,
    source_snapshot_id UUID REFERENCES raw_quikstrike_snapshots(id)
);

-- Computed OI features for overlay
CREATE TABLE IF NOT EXISTS oi_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    instrument TEXT NOT NULL,
    nearest_expiry_date DATE NOT NULL,
    nearest_dte INTEGER NOT NULL,
    top_put_strikes JSONB NOT NULL,
    top_call_strikes JSONB NOT NULL,
    pin_candidate_strike NUMERIC NULL,
    spot_at_compute NUMERIC NULL,
    rules_version TEXT NOT NULL DEFAULT 'v1.0'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_oi_strikes_instrument_dte ON oi_strikes(instrument, dte, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_oi_features_instrument_computed ON oi_features(instrument, computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_snapshots_instrument_scraped ON raw_quikstrike_snapshots(instrument, scraped_at DESC);