"""
Continuous Database Health Monitor
Runs as a background service to detect and fix database issues
"""
import os
import time
import logging
from datetime import datetime
from database.railway_db import RailwayDB
from psycopg2 import extensions

# Feature gating - matches web_server.py pattern
ENABLE_LEGACY = os.environ.get("ENABLE_LEGACY", "false").lower() == "true"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseHealthMonitor:
    def __init__(self, check_interval=30):
        """
        Initialize database health monitor
        
        Args:
            check_interval: Seconds between health checks (default: 30)
        """
        self.check_interval = check_interval
        self.db = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.last_check_time = None
        self.stats = {
            'total_checks': 0,
            'healthy_checks': 0,
            'aborted_transactions_fixed': 0,
            'reconnections': 0,
            'errors': 0
        }
    
    def connect_database(self):
        """Connect or reconnect to database"""
        try:
            self.db = RailwayDB()
            if self.db and self.db.conn:
                logger.info("✅ Database connected")
                self.consecutive_errors = 0
                return True
            else:
                logger.error("❌ Database connection failed")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def check_transaction_status(self):
        """Check and fix transaction status"""
        if not self.db or not self.db.conn:
            return False
        
        try:
            status = self.db.conn.get_transaction_status()
            
            if status == extensions.TRANSACTION_STATUS_INERROR:
                logger.warning("⚠️ ABORTED TRANSACTION DETECTED - Auto-fixing...")
                self.db.conn.rollback()
                self.stats['aborted_transactions_fixed'] += 1
                logger.info("✅ Aborted transaction rolled back")
                return True
                
            elif status == extensions.TRANSACTION_STATUS_INTRANS:
                logger.warning("⚠️ Open transaction detected - committing...")
                self.db.conn.commit()
                logger.info("✅ Open transaction committed")
                return True
                
            elif status == extensions.TRANSACTION_STATUS_IDLE:
                # This is good - no action needed
                return True
                
            else:
                logger.warning(f"⚠️ Unusual transaction status: {status}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking transaction: {e}")
            return False
    
    def test_database_query(self):
        """Test database with a simple query"""
        if not self.db or not self.db.conn:
            return False
        
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"❌ Test query failed: {e}")
            return False
    
    def check_recent_signals(self):
        """Check if signals are flowing (legacy live_signals table)"""
        # Gate legacy live_signals queries
        if not ENABLE_LEGACY:
            logger.warning("⚠️ Legacy signal health checks disabled (ENABLE_LEGACY=false)")
            return {"healthy": True, "message": "Legacy checks disabled"}
        
        if not self.db or not self.db.conn:
            return None
        
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT 
                    MAX(timestamp) as last_signal,
                    COUNT(*) as total_signals
                FROM live_signals
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)
            result = cursor.fetchone()
            
            if result:
                return {
                    'last_signal': result['last_signal'],
                    'signals_last_hour': result['total_signals']
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking signals: {e}")
            return None
    
    def perform_health_check(self):
        """Perform comprehensive health check"""
        self.stats['total_checks'] += 1
        self.last_check_time = datetime.now()
        
        logger.info(f"🔍 Health check #{self.stats['total_checks']}")
        
        # Step 1: Check connection
        if not self.db or not self.db.conn:
            logger.warning("⚠️ No database connection - reconnecting...")
            if not self.connect_database():
                self.consecutive_errors += 1
                self.stats['errors'] += 1
                return False
            self.stats['reconnections'] += 1
        
        # Step 2: Check transaction status
        if not self.check_transaction_status():
            logger.warning("⚠️ Transaction status check failed")
            self.consecutive_errors += 1
            self.stats['errors'] += 1
            return False
        
        # Step 3: Test with query
        if not self.test_database_query():
            logger.warning("⚠️ Test query failed - reconnecting...")
            if self.connect_database():
                self.stats['reconnections'] += 1
            else:
                self.consecutive_errors += 1
                self.stats['errors'] += 1
                return False
        
        # Step 4: Check signal flow
        signal_info = self.check_recent_signals()
        if signal_info:
            logger.info(f"📊 Signals last hour: {signal_info['signals_last_hour']}")
            if signal_info['last_signal']:
                time_since = datetime.now() - signal_info['last_signal'].replace(tzinfo=None)
                minutes = int(time_since.total_seconds() / 60)
                if minutes > 15:
                    logger.warning(f"⚠️ No signals for {minutes} minutes")
                else:
                    logger.info(f"✅ Last signal: {minutes}m ago")
        
        # Success!
        self.stats['healthy_checks'] += 1
        self.consecutive_errors = 0
        logger.info("✅ Health check passed")
        
        return True
    
    def print_stats(self):
        """Print monitoring statistics"""
        uptime_pct = (self.stats['healthy_checks'] / self.stats['total_checks'] * 100) if self.stats['total_checks'] > 0 else 0
        
        logger.info("=" * 60)
        logger.info("📊 DATABASE HEALTH MONITOR STATS")
        logger.info("=" * 60)
        logger.info(f"Total checks: {self.stats['total_checks']}")
        logger.info(f"Healthy checks: {self.stats['healthy_checks']} ({uptime_pct:.1f}%)")
        logger.info(f"Aborted transactions fixed: {self.stats['aborted_transactions_fixed']}")
        logger.info(f"Reconnections: {self.stats['reconnections']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Last check: {self.last_check_time}")
        logger.info("=" * 60)
    
    def run(self):
        """Run continuous monitoring"""
        logger.info("🚀 Database Health Monitor started")
        logger.info(f"⏰ Check interval: {self.check_interval} seconds")
        
        # Initial connection
        if not self.connect_database():
            logger.error("❌ Failed to connect to database on startup")
            return
        
        check_count = 0
        
        try:
            while True:
                # Perform health check
                self.perform_health_check()
                
                # Print stats every 10 checks
                check_count += 1
                if check_count % 10 == 0:
                    self.print_stats()
                
                # Check if too many consecutive errors
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.error(f"❌ {self.consecutive_errors} consecutive errors - attempting recovery...")
                    self.connect_database()
                    self.consecutive_errors = 0
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitor stopped by user")
            self.print_stats()
        except Exception as e:
            logger.error(f"❌ Monitor crashed: {e}")
            self.print_stats()

if __name__ == '__main__':
    # Run with 30 second intervals
    monitor = DatabaseHealthMonitor(check_interval=30)
    monitor.run()
