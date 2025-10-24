"""
Automatic ML Hyperparameter Optimization
Runs in background, triggers optimization based on conditions
"""
import threading
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AutoMLOptimizer:
    def __init__(self, db, check_interval=3600):
        self.db = db
        self.check_interval = check_interval  # 1 hour default
        self.last_optimization_time = None
        self.last_sample_count = 0
        self.running = False
        self.first_run = True
        
    def should_optimize(self):
        """Check if optimization should run"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
            current_count = cursor.fetchone()['count']
            
            logger.info(f"📊 Sample check: {current_count} samples available")
            
            # First optimization: 500+ samples (run immediately)
            if self.last_optimization_time is None and current_count >= 500:
                logger.info(f"🔧 TRIGGER: First optimization with {current_count} samples (threshold: 500)")
                return True
            
            # 200+ new samples since last optimization
            if self.last_sample_count > 0 and current_count - self.last_sample_count >= 200:
                logger.info(f"🔧 TRIGGER: {current_count - self.last_sample_count} new samples (threshold: 200)")
                return True
            
            # Monthly optimization
            if self.last_optimization_time:
                days_since = (datetime.now() - self.last_optimization_time).days
                if days_since >= 30:
                    logger.info(f"🔧 TRIGGER: Monthly optimization ({days_since} days since last run)")
                    return True
            
            logger.info(f"⏸️ No optimization needed: {current_count} samples, last_count={self.last_sample_count}, last_run={self.last_optimization_time}")
            return False
        except Exception as e:
            logger.error(f"Error checking optimization conditions: {str(e)}")
            return False
    
    def run_optimization(self):
        """Run hyperparameter optimization"""
        try:
            from ml_hyperparameter_optimizer import optimize_trading_models
            import json
            
            logger.info("🚀 Starting automatic hyperparameter optimization...")
            start_time = time.time()
            results = optimize_trading_models(self.db)
            duration = time.time() - start_time
            
            if 'error' not in results:
                rf_imp = results['comparison']['rf_improvement']['accuracy']
                gb_imp = results['comparison']['gb_improvement']['accuracy']
                logger.info(f"✅ Optimization complete: RF +{rf_imp:.2f}%, GB +{gb_imp:.2f}%")
                
                # Store results in database
                cursor = self.db.conn.cursor()
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
                    rf_imp,
                    duration
                ))
                self.db.conn.commit()
                
                self.last_optimization_time = datetime.now()
                cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
                self.last_sample_count = cursor.fetchone()['count']
            else:
                logger.error(f"❌ Optimization failed: {results['error']}")
                
        except Exception as e:
            logger.error(f"❌ Optimization error: {str(e)}")
            if hasattr(self.db, 'conn'):
                self.db.conn.rollback()
    
    def monitor_loop(self):
        """Background monitoring loop"""
        logger.info("🔍 Auto-optimizer started - checking immediately...")
        
        while self.running:
            try:
                # Check immediately on first run, then hourly
                if self.first_run:
                    logger.info("🚀 First run - checking optimization conditions immediately")
                    self.first_run = False
                    if self.should_optimize():
                        self.run_optimization()
                    else:
                        logger.info("⏸️ Conditions not met for first optimization")
                else:
                    if self.should_optimize():
                        self.run_optimization()
                
                logger.info(f"⏰ Next check in {self.check_interval} seconds")
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitor error: {str(e)}")
                time.sleep(60)
    
    def start(self):
        """Start background optimizer"""
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self.monitor_loop, daemon=True)
            thread.start()
            logger.info("✅ Auto-optimizer thread started")
    
    def stop(self):
        """Stop background optimizer"""
        self.running = False

def start_auto_optimizer(db):
    """Initialize and start auto-optimizer"""
    optimizer = AutoMLOptimizer(db, check_interval=3600)  # Check every hour
    optimizer.start()
    return optimizer
