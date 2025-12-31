-- Phase D.1: Generalize Symbol Registry for Any Symbol
-- Purpose: Add optional metadata columns to support diverse asset classes without schema changes

-- Add vendor_dataset column (nullable for backward compatibility)
ALTER TABLE symbol_registry 
ADD COLUMN IF NOT EXISTS vendor_dataset TEXT;

-- Add schema_name column (nullable, defaults handled in code)
ALTER TABLE symbol_registry 
ADD COLUMN IF NOT EXISTS schema_name TEXT;

-- Add venue column (optional metadata)
ALTER TABLE symbol_registry 
ADD COLUMN IF NOT EXISTS venue TEXT;

-- Add asset_class column (optional metadata)
ALTER TABLE symbol_registry 
ADD COLUMN IF NOT EXISTS asset_class TEXT;

-- Add timezone column (optional metadata for session handling)
ALTER TABLE symbol_registry 
ADD COLUMN IF NOT EXISTS timezone TEXT;

-- Add session_profile column (optional metadata for trading sessions)
ALTER TABLE symbol_registry 
ADD COLUMN IF NOT EXISTS session_profile TEXT;

-- Update existing rows to populate vendor_dataset (same as dataset for now)
UPDATE symbol_registry 
SET vendor_dataset = dataset 
WHERE vendor_dataset IS NULL;

-- Update existing rows to populate schema_name (same as schema for now)
UPDATE symbol_registry 
SET schema_name = schema 
WHERE schema_name IS NULL;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_symbol_registry_vendor_dataset ON symbol_registry(vendor_dataset);
CREATE INDEX IF NOT EXISTS idx_symbol_registry_asset_class ON symbol_registry(asset_class);
CREATE INDEX IF NOT EXISTS idx_symbol_registry_venue ON symbol_registry(venue);

-- Add comments
COMMENT ON COLUMN symbol_registry.vendor_dataset IS 'Vendor-specific dataset identifier (e.g., GLBX.MDP3, CME.MDP3)';
COMMENT ON COLUMN symbol_registry.schema_name IS 'Data schema name (e.g., ohlcv-1m, trades, quotes)';
COMMENT ON COLUMN symbol_registry.venue IS 'Trading venue (e.g., CME, NYMEX, COMEX, ICE)';
COMMENT ON COLUMN symbol_registry.asset_class IS 'Asset class (e.g., equity_index, energy, metals, fx, crypto)';
COMMENT ON COLUMN symbol_registry.timezone IS 'Primary trading timezone (e.g., America/Chicago, America/New_York)';
COMMENT ON COLUMN symbol_registry.session_profile IS 'Session profile name for trading hours (e.g., cme_equity_index, nymex_energy)';

-- Update existing symbols with metadata
UPDATE symbol_registry SET venue = 'CME', asset_class = 'equity_index', timezone = 'America/Chicago' WHERE root IN ('NQ', 'ES', 'YM', 'RTY');
