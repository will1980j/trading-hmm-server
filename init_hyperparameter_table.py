"""Initialize hyperparameter optimization results table"""
import logging

logger = logging.getLogger(__name__)

def init_hyperparameter_table(db):
    """Create hyperparameter_optimization_results table if it doesn't exist"""
    try:
        cursor = db.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hyperparameter_optimization_results (
                id SERIAL PRIMARY KEY,
                optimization_timestamp TIMESTAMP DEFAULT NOW(),
                rf_params JSONB,
                gb_params JSONB,
                baseline_accuracy REAL,
                optimized_accuracy REAL,
                improvement_pct REAL,
                optimization_duration_seconds REAL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hyperparam_timestamp 
            ON hyperparameter_optimization_results(optimization_timestamp DESC)
        """)
        
        db.conn.commit()
        logger.info("✅ Hyperparameter optimization table initialized")
        
    except Exception as e:
        db.conn.rollback()
        logger.error(f"Failed to initialize hyperparameter table: {str(e)}")
