-- Run these in Supabase SQL Editor

-- Market data table
CREATE TABLE market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    volume BIGINT,
    timeframe VARCHAR(5) DEFAULT '1m',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trading signals table
CREATE TABLE trading_signals (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(12,4),
    stop_loss DECIMAL(12,4),
    take_profit DECIMAL(12,4),
    confidence DECIMAL(3,2),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'active',
    result JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ICT levels table
CREATE TABLE ict_levels (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    level_type VARCHAR(20) NOT NULL,
    price_high DECIMAL(12,4),
    price_low DECIMAL(12,4),
    strength DECIMAL(3,2),
    active BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_market_data_symbol_time ON market_data(symbol, timestamp DESC);
CREATE INDEX idx_signals_symbol_status ON trading_signals(symbol, status);
CREATE INDEX idx_levels_symbol_active ON ict_levels(symbol, active);

-- Enable Row Level Security (optional)
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE ict_levels ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (adjust as needed)
CREATE POLICY "Allow all" ON market_data FOR ALL USING (true);
CREATE POLICY "Allow all" ON trading_signals FOR ALL USING (true);
CREATE POLICY "Allow all" ON ict_levels FOR ALL USING (true);