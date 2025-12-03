-- Add MAE (Maximum Adverse Excursion) column to automated_signals table
-- MAE tracks the worst drawdown in R-multiples during a trade

ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS mae_global_r FLOAT DEFAULT NULL;

-- Add comment for documentation
COMMENT ON COLUMN automated_signals.mae_global_r IS 'Maximum Adverse Excursion in R-multiples (worst drawdown during trade)';
