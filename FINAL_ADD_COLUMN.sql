-- FINAL SOLUTION: Add target_r_score column
-- Copy and paste this into Railway database console

ALTER TABLE signal_lab_trades 
ADD COLUMN target_r_score DECIMAL(5,2) DEFAULT NULL;

-- Verify it was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'signal_lab_trades' 
AND column_name = 'target_r_score';