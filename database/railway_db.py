"""Railway PostgreSQL database connection with resilient error handling"""
import logging
import os
import psycopg2
from psycopg2 import pool, extensions
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Try to import resilient system, fall back to basic connection
try:
    from database.resilient_connection import get_resilient_db
    RESILIENT_AVAILABLE = True
except ImportError:
    RESILIENT_AVAILABLE = False
    logger.warning("Resilient connection system not available, using basic connection")

class RailwayDB:
    def __init__(self, use_pool=True):
        if RESILIENT_AVAILABLE:
            self._resilient_db = get_resilient_db()
            self.conn = self._resilient_db.conn
            self._using_resilient = True
        else:
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                self.conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
                self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_READ_COMMITTED)
                self.conn.rollback()
            else:
                self.conn = None
            self._using_resilient = False
    
    def close(self):
        if not self._using_resilient and self.conn:
            try:
                self.conn.close()
            except:
                pass
    
    def __del__(self):
        self.close()
    
    def ensure_clean_transaction(self):
        if self._using_resilient:
            self._resilient_db._check_and_fix_transaction_state()
        elif self.conn:
            try:
                status = self.conn.get_transaction_status()
                if status == extensions.TRANSACTION_STATUS_INERROR:
                    self.conn.rollback()
            except:
                pass
        return True
    
    def store_market_data(self, symbol, data):
        """Mock store market data"""
        logger.info(f"Mock: Storing market data for {symbol}")
        return True
    
    def store_signal(self, signal_data):
        """Mock store signal"""
        logger.info(f"Mock: Storing signal {signal_data.get('type', 'Unknown')}")
        return True
    
    def store_ict_level(self, level_data):
        """Mock store ICT level"""
        logger.info(f"Mock: Storing ICT level {level_data.get('type', 'Unknown')}")
        return True