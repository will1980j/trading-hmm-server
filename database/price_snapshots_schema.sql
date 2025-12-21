-- Price Snapshots Table for Backend MFE/MAE Calculation

CREATE TABLE IF NOT EXISTS price_snapshots (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL DEFAULT '1m',
    bar_ts BIGINT NOT NULL,
    open NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2) NOT NULL,
    low NUMERIC(12, 2) NOT NULL,
    close NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, bar_ts)
);

CREATE INDEX IF NOT EXISTS idx_price_snapshots_symbol_ts ON price_snapshots(symbol, bar_ts DESC);
CREATE INDEX IF NOT EXISTS idx_price_snapshots_created ON price_snapshots(created_at DESC);

-- Add symbol column to confirmed_signals_ledger if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'confirmed_signals_ledger' 
        AND column_name = 'symbol'
    ) THEN
        ALTER TABLE confirmed_signals_ledger 
        ADD COLUMN symbol VARCHAR(50) DEFAULT 'NQH2025';
    END IF;
END $$;

-- Add risk_r column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'confirmed_signals_ledger' 
        AND column_name = 'risk_r'
    ) THEN
        ALTER TABLE confirmed_signals_ledger 
        ADD COLUMN risk_r NUMERIC(12, 4);
        
        -- Backfill risk_r from entry_price and stop_price
        UPDATE confirmed_signals_ledger
        SET risk_r = ABS(entry_price - stop_price)
        WHERE entry_price IS NOT NULL 
        AND stop_price IS NOT NULL
        AND risk_r IS NULL;
    END IF;
END $$;

-- Add completed_at column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'confirmed_signals_ledger' 
        AND column_name = 'completed_at'
    ) THEN
        ALTER TABLE confirmed_signals_ledger 
        ADD COLUMN completed_at TIMESTAMP;
    END IF;
END $$;
