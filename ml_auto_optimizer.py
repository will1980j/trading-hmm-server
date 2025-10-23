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
        
    def should_optimize(self):
        """Check if optimization should run"""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
        current_count = cursor.fetchone()['count']
        
        # First optimization: 500+ samples
        if self.last_optimization_time is None and current_count >= 500:
            logger.info(f"🔧 First optimization: {current_count} samples")
            return True
        
        # 200+ new samples since last optimization
        if current_count - self.last_sample_count >= 200:
            logger.info(f"🔧 200+ new samples: {current_count - self.last_sample_count}")
            return True
        
        # Monthly optimization
        if self.last_optimization_time:
            days_since = (datetime.now() - self.last_optimization_time).days
            if days_since >= 30:
                logger.info(f"🔧 Monthly optimization: {days_since} days")
                return True
        
        return False
    
    def run_optimization(self):
        """Run hyperparameter optimization"""
        try:
            from ml_hyperparameter_optimizer import optimize_trading_models
            
            logger.info("🚀 Starting automatic hyperparameter optimization...")
            results = optimize_trading_models(self.db)
            
            if 'error' not in results:
                rf_imp = results['comparison']['rf_improvement']['accuracy']
                gb_imp = results['comparison']['gb_improvement']['accuracy']
                logger.info(f"✅ Optimization complete: RF +{rf_imp:.2f}%, GB +{gb_imp:.2f}%")
                
                self.last_optimization_time = datetime.now()
                cursor = self.db.conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
                self.last_sample_count = cursor.fetchone()['count']
            else:
                logger.error(f"❌ Optimization failed: {results['error']}")
                
        except Exception as e:
            logger.error(f"❌ Optimization error: {str(e)}")
    
    def monitor_loop(self):
        """Background monitoring loop"""
        logger.info("🔍 Auto-optimizer started")
        
        while self.running:
            try:
                if self.should_optimize():
                    self.run_optimization()
                
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
