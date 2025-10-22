"""Railway PostgreSQL database connection"""
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import extensions

logger = logging.getLogger(__name__)

class RailwayDB:
    def __init__(self):
        try:
            # Railway provides DATABASE_URL environment variable
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                # Set autocommit=False for explicit transaction control
                self.conn = psycopg2.connect(
                    database_url, 
                    cursor_factory=RealDictCursor
                )
                # Set isolation level to READ COMMITTED (default, but explicit)
                self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_READ_COMMITTED)
                logger.info("Connected to Railway PostgreSQL database")
                
                # Always start with a clean slate
                try:
                    self.conn.rollback()
                    logger.info("Initial transaction rollback completed")
                except:
                    pass
            else:
                self.conn = None
                logger.warning("No DATABASE_URL found - using mock database")
        except Exception as e:
            self.conn = None
            logger.error(f"Database connection failed: {e}")
    
    def ensure_clean_transaction(self):
        """Ensure we're not in an aborted transaction state"""
        if self.conn:
            try:
                # Check transaction status
                status = self.conn.get_transaction_status()
                if status == extensions.TRANSACTION_STATUS_INERROR:
                    logger.warning("⚠️ Aborted transaction detected - rolling back")
                    self.conn.rollback()
                    return True
                elif status == extensions.TRANSACTION_STATUS_INTRANS:
                    # In transaction but not aborted - commit it
                    logger.info("🔄 Open transaction detected - committing")
                    self.conn.commit()
                    return True
                return False
            except Exception as e:
                logger.error(f"Error checking transaction status: {e}")
                try:
                    self.conn.rollback()
                except:
                    pass
                return False
        return False
    
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