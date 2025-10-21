-- Run this SQL directly on Railway database

CREATE TABLE IF NOT EXISTS webhook_debug_log (
    id SERIAL PRIMARY KEY,
    raw_payload TEXT,
    parsed_data JSONB,
    source VARCHAR(50) DEFAULT 'TradingView',
    received_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signal_processing_log (
    id SERIAL PRIMARY KEY,
    bias VARCHAR(20),
    symbol VARCHAR(20),
    price DECIMAL(10, 4),
    status VARCHAR(20),
    error_message TEXT,
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_webhook_debug_received ON webhook_debug_log(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_signal_processing_bias ON signal_processing_log(bias, processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_signal_processing_status ON signal_processing_log(status, processed_at DESC);
