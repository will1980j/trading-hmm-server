"""
Force Hyperparameter Optimization - Run Immediately
"""
import sys
import logging
from database.railway_db import RailwayDB
from ml_hyperparameter_optimizer import optimize_trading_models
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_optimization():
    """Force hyperparameter optimization to run immediately"""
    try:
        logger.info("🚀 FORCE OPTIMIZATION STARTED")
        
        # Connect to database
        db = RailwayDB()
        logger.info("✅ Database connected")
        
        # Check sample count
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
        sample_count = cursor.fetchone()['count']
        logger.info(f"📊 Found {sample_count} samples for training")
        
        if sample_count < 100:
            logger.error(f"❌ Insufficient samples: {sample_count} (need at least 100)")
            return
        
        # Run optimization
        logger.info("🔧 Starting hyperparameter optimization...")
        start_time = time.time()
        
        results = optimize_trading_models(db)
        
        duration = time.time() - start_time
        
        if 'error' in results:
            logger.error(f"❌ Optimization failed: {results['error']}")
            return
        
        # Store results
        logger.info("💾 Storing optimization results...")
        cursor.execute("""
            INSERT INTO hyperparameter_optimization_results 
            (rf_params, gb_params, baseline_accuracy, optimized_accuracy, 
             improvement_pct, optimization_duration_seconds)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            json.dumps(results['rf_optimization']['best_params']),
            json.dumps(results['gb_optimization']['best_params']),
            results['comparison']['baseline_rf']['accuracy'],
            results['comparison']['optimized_rf']['accuracy'],
            results['comparison']['rf_improvement']['accuracy'],
            duration
        ))
        db.conn.commit()
        
        logger.info("✅ OPTIMIZATION COMPLETE!")
        logger.info(f"📈 RF Improvement: +{results['comparison']['rf_improvement']['accuracy']:.2f}%")
        logger.info(f"📈 GB Improvement: +{results['comparison']['gb_improvement']['accuracy']:.2f}%")
        logger.info(f"⏱️ Duration: {duration:.1f} seconds")
        logger.info(f"🎯 Best RF params: {results['rf_optimization']['best_params']}")
        logger.info(f"🎯 Best GB params: {results['gb_optimization']['best_params']}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Force optimization error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    force_optimization()
