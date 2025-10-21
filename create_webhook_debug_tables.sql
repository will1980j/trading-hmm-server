-- Webhook Debug Logging Tables

-- Table for all incoming webhook requests
CREATE TABLE IF NOT EXISTS webhook_debug_log (
    id SERIAL PRIMARY KEY,
    raw_payload TEXT,
    parsed_data JSONB,
    source VARCHAR(50) DEFAULT 'TradingView',
    received_at TIMESTAMP DEFAULT NOW()
);

-- Table for signal processing results
CREATE TABLE IF NOT EXISTS signal_processing_log (
    id SERIAL PRIMARY KEY,
    bias VARCHAR(20),
    symbol VARCHAR(20),
    price DECIMAL(10, 4),
    status VARCHAR(20),
    error_message TEXT,
    processed_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_webhook_debug_received ON webhook_debug_log(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_signal_processing_bias ON signal_processing_log(bias, processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_signal_processing_status ON signal_processing_log(status, processed_at DESC);

-- View for quick signal stats
CREATE OR REPLACE VIEW signal_stats_24h AS
SELECT 
    bias,
    COUNT(*) as total_signals,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    MAX(processed_at) as last_signal
FROM signal_processing_log
WHERE processed_at > NOW() - INTERVAL '24 hours'
GROUP BY bias;
