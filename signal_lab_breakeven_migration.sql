-- Signal Lab Breakeven Migration
-- Add new breakeven tracking columns to signal_lab_trades table

-- Add new columns for enhanced breakeven tracking
ALTER TABLE signal_lab_trades 
ADD COLUMN IF NOT EXISTS mfe_none DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS be1_level DECIMAL(10,2) DEFAULT 1,
ADD COLUMN IF NOT EXISTS be1_hit BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS mfe1 DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS be2_level DECIMAL(10,2) DEFAULT 2,
ADD COLUMN IF NOT EXISTS be2_hit BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS mfe2 DECIMAL(10,2) DEFAULT 0;

-- Migrate existing MFE data to mfe_none column
UPDATE signal_lab_trades 
SET mfe_none = COALESCE(mfe, 0)
WHERE mfe_none = 0 AND mfe IS NOT NULL;

-- Optional: Remove old columns after confirming migration works
-- ALTER TABLE signal_lab_trades DROP COLUMN IF EXISTS be_achieved;
-- ALTER TABLE signal_lab_trades DROP COLUMN IF EXISTS breakeven;
-- ALTER TABLE signal_lab_trades DROP COLUMN IF EXISTS mfe;