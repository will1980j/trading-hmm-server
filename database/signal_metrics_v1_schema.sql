-- Signal Metrics V1 - Computed MFE/MAE from Databento OHLCV
CREATE TABLE IF NOT EXISTS signal_metrics_v1 (
    trade_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction_norm TEXT NOT NULL,
    entry_bar_open_ts TIMESTAMPTZ NOT NULL,
    exit_bar_open_ts TIMESTAMPTZ,
    entry_price NUMERIC NOT NULL,
    stop_loss NUMERIC NOT NULL,
    risk_distance NUMERIC NOT NULL,
    no_be_mfe NUMERIC NOT NULL,
    be_mfe NUMERIC NOT NULL,
    mae_global_r NUMERIC NOT NULL,
    highest_high NUMERIC,
    lowest_low NUMERIC,
    be_triggered BOOLEAN NOT NULL,
    be_trigger_bar_open_ts TIMESTAMPTZ,
    computed_window_start_ts TIMESTAMPTZ NOT NULL,
    computed_window_end_ts TIMESTAMPTZ NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logic_version TEXT NOT NULL DEFAULT 'signal_metrics_v1'
);

CREATE INDEX IF NOT EXISTS idx_signal_metrics_symbol_entry ON signal_metrics_v1(symbol, entry_bar_open_ts);
CREATE INDEX IF NOT EXISTS idx_signal_metrics_computed_at ON signal_metrics_v1(computed_at);
