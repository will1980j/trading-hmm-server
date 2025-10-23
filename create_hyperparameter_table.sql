-- Hyperparameter Optimization Results Table
CREATE TABLE IF NOT EXISTS hyperparameter_optimization_results (
    id SERIAL PRIMARY KEY,
    optimization_timestamp TIMESTAMP DEFAULT NOW(),
    rf_params JSONB,
    gb_params JSONB,
    baseline_accuracy REAL,
    optimized_accuracy REAL,
    improvement_pct REAL,
    optimization_duration_seconds REAL
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_hyperparam_timestamp 
ON hyperparameter_optimization_results(optimization_timestamp DESC);
