-- Add separate BE=1 and No BE MFE columns to automated_signals table

ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS be_mfe FLOAT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS no_be_mfe FLOAT DEFAULT NULL;

-- Update existing records: copy current mfe to no_be_mfe (since current system doesn't use BE)
UPDATE automated_signals 
SET no_be_mfe = mfe 
WHERE no_be_mfe IS NULL AND mfe IS NOT NULL;

-- Add comment for clarity
COMMENT ON COLUMN automated_signals.be_mfe IS 'MFE with Break-Even at +1R (stops at entry after +1R achieved)';
COMMENT ON COLUMN automated_signals.no_be_mfe IS 'MFE without Break-Even (continues until original stop loss)';
COMMENT ON COLUMN automated_signals.mfe IS 'Legacy MFE column - use be_mfe and no_be_mfe instead';
