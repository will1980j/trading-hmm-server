"""Railway PostgreSQL database connection with resilient error handling"""
import logging
from database.resilient_connection import ResilientDatabaseConnection, get_resilient_db

logger = logging.getLogger(__name__)

class RailwayDB:
    """
    Wrapper for ResilientDatabaseConnection to maintain backward compatibility
    All database operations now use the resilient connection system
    """
    def __init__(self, use_pool=True):
        self._resilient_db = get_resilient_db()
        self.conn = self._resilient_db.conn
    
    def close(self):
        pass  # Resilient connection manages its own lifecycle
    
    def __del__(self):
        pass  # Resilient connection manages its own lifecycle
    
    def ensure_clean_transaction(self):
        self._resilient_db._check_and_fix_transaction_state()
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