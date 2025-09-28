-- Prop Firm Management Database Schema
-- Phase 1 MVP Tables

-- Prop Firms Registry
CREATE TABLE prop_firms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    base_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    max_drawdown DECIMAL(12,2) NOT NULL,
    daily_loss_limit DECIMAL(12,2) NOT NULL,
    profit_target DECIMAL(12,2) NOT NULL,
    contract_cap INTEGER DEFAULT 10,
    drawdown_type VARCHAR(20) DEFAULT 'trailing', -- 'trailing' or 'static'
    payout_frequency VARCHAR(20) DEFAULT 'weekly', -- 'weekly', 'monthly'
    payout_split_percent DECIMAL(5,2) DEFAULT 80.00, -- Trader's percentage
    minimum_withdrawal DECIMAL(10,2) DEFAULT 100.00,
    platforms JSONB DEFAULT '[]', -- ['Rithmic', 'NinjaTrader', 'Tradovate']
    scaling_rules JSONB DEFAULT '{}', -- Scaling milestones and rules
    automation_support JSONB DEFAULT '{}', -- Copier, webhook, API support
    rule_version VARCHAR(20) DEFAULT '2025-01-01',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prop Trading Accounts
CREATE TABLE prop_accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL UNIQUE, -- External account ID (e.g., APX-123456)
    firm_id INTEGER REFERENCES prop_firms(id) ON DELETE CASCADE,
    user_id VARCHAR(100), -- Future: link to user management
    status VARCHAR(20) DEFAULT 'evaluation', -- 'evaluation', 'active', 'paused', 'violation', 'closed'
    balance DECIMAL(12,2) NOT NULL,
    equity DECIMAL(12,2) NOT NULL,
    peak_equity DECIMAL(12,2) NOT NULL, -- For trailing drawdown calculation
    current_drawdown DECIMAL(12,2) DEFAULT 0.00,
    daily_pnl DECIMAL(12,2) DEFAULT 0.00,
    daily_loss_counter DECIMAL(12,2) DEFAULT 0.00, -- Reset daily
    contract_limit INTEGER DEFAULT 10,
    evaluation_stage VARCHAR(20) DEFAULT 'stage1', -- 'stage1', 'stage2', 'funded'
    evaluation_progress DECIMAL(5,2) DEFAULT 0.00, -- Percentage towards profit target
    last_trade_date DATE,
    last_payout_date DATE,
    copier_provider VARCHAR(50), -- 'DXTrade', 'Tradovate', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading Activity (simplified for MVP)
CREATE TABLE prop_trades (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) REFERENCES prop_accounts(account_id) ON DELETE CASCADE,
    firm_id INTEGER REFERENCES prop_firms(id) ON DELETE CASCADE,
    trade_timestamp TIMESTAMP NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL, -- 'long', 'short'
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(10,4),
    exit_price DECIMAL(10,4),
    pnl DECIMAL(12,2) DEFAULT 0.00,
    commission DECIMAL(8,2) DEFAULT 0.00,
    session_tag VARCHAR(20), -- 'Asia', 'London', 'NY'
    strategy_id VARCHAR(50),
    violation_flag BOOLEAN DEFAULT FALSE,
    violation_reasons JSONB DEFAULT '[]',
    raw_payload JSONB, -- Store original webhook data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compliance Violations
CREATE TABLE prop_violations (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) REFERENCES prop_accounts(account_id) ON DELETE CASCADE,
    firm_id INTEGER REFERENCES prop_firms(id) ON DELETE CASCADE,
    violation_type VARCHAR(50) NOT NULL, -- 'drawdown', 'daily_loss', 'contract_cap', 'time_filter'
    description TEXT NOT NULL,
    violation_amount DECIMAL(12,2), -- Amount that caused violation
    limit_amount DECIMAL(12,2), -- The limit that was breached
    severity VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Evaluation Progress Tracking
CREATE TABLE prop_evaluations (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) REFERENCES prop_accounts(account_id) ON DELETE CASCADE,
    firm_id INTEGER REFERENCES prop_firms(id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL, -- 'stage1', 'stage2', 'funded'
    target_profit DECIMAL(12,2) NOT NULL,
    current_profit DECIMAL(12,2) DEFAULT 0.00,
    progress_percent DECIMAL(5,2) DEFAULT 0.00,
    days_elapsed INTEGER DEFAULT 0,
    max_days INTEGER, -- Time limit for stage
    passed BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT
);

-- Payout Management
CREATE TABLE prop_payouts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) REFERENCES prop_accounts(account_id) ON DELETE CASCADE,
    firm_id INTEGER REFERENCES prop_firms(id) ON DELETE CASCADE,
    amount_original DECIMAL(12,2) NOT NULL, -- In firm's base currency
    currency_original VARCHAR(3) NOT NULL,
    amount_aud DECIMAL(12,2), -- Converted to AUD
    fx_rate DECIMAL(10,6), -- Exchange rate used
    split_percent DECIMAL(5,2) NOT NULL, -- Trader's percentage
    trader_amount DECIMAL(12,2) NOT NULL, -- Amount to trader
    firm_amount DECIMAL(12,2) NOT NULL, -- Amount to firm
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'paid', 'rejected'
    payment_method VARCHAR(50), -- 'bank_transfer', 'paypal', 'crypto'
    payment_reference VARCHAR(100),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    notes TEXT
);

-- FX Rates (for AUD conversion)
CREATE TABLE fx_rates (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) NOT NULL, -- 'USD/AUD', 'EUR/AUD'
    rate DECIMAL(10,6) NOT NULL,
    source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'api', 'bank'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_prop_accounts_firm_id ON prop_accounts(firm_id);
CREATE INDEX idx_prop_accounts_status ON prop_accounts(status);
CREATE INDEX idx_prop_trades_account_id ON prop_trades(account_id);
CREATE INDEX idx_prop_trades_timestamp ON prop_trades(trade_timestamp);
CREATE INDEX idx_prop_violations_account_id ON prop_violations(account_id);
CREATE INDEX idx_prop_violations_created_at ON prop_violations(created_at);
CREATE INDEX idx_prop_payouts_account_id ON prop_payouts(account_id);
CREATE INDEX idx_prop_payouts_status ON prop_payouts(status);

-- Sample data for testing
INSERT INTO prop_firms (name, base_currency, max_drawdown, daily_loss_limit, profit_target, contract_cap) VALUES
('Apex Trader Funding', 'USD', 2500.00, 1000.00, 5000.00, 10),
('FTMO', 'USD', 5000.00, 2500.00, 10000.00, 15),
('The5ers', 'USD', 3000.00, 1500.00, 6000.00, 12),
('MyForexFunds', 'USD', 6000.00, 3000.00, 12000.00, 20);

-- Sample accounts for testing
INSERT INTO prop_accounts (account_id, firm_id, balance, equity, peak_equity, status) VALUES
('APX-123456', 1, 50000.00, 52500.00, 52500.00, 'active'),
('FTMO-789012', 2, 100000.00, 98500.00, 103000.00, 'active'),
('T5-345678', 3, 60000.00, 61200.00, 61200.00, 'evaluation'),
('MFF-901234', 4, 120000.00, 115000.00, 125000.00, 'violation');

-- Sample violations for testing
INSERT INTO prop_violations (account_id, firm_id, violation_type, description, violation_amount, limit_amount) VALUES
('MFF-901234', 4, 'drawdown', 'Account exceeded maximum drawdown limit', 10000.00, 6000.00),
('APX-123456', 1, 'daily_loss', 'Daily loss limit exceeded', 1200.00, 1000.00);