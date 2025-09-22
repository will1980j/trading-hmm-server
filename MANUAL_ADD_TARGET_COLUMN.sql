-- Manual SQL script to add target_r_score column to signal_lab_trades table
-- Run this directly in Railway database console

-- Check if column already exists
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'signal_lab_trades' 
AND column_name = 'target_r_score';

-- Add the target_r_score column if it doesn't exist
ALTER TABLE signal_lab_trades 
ADD COLUMN IF NOT EXISTS target_r_score DECIMAL(5,2) DEFAULT NULL;

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'signal_lab_trades' 
AND column_name = 'target_r_score';

-- Show table structure to confirm
\d signal_lab_trades;