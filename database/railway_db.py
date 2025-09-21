"""Railway PostgreSQL database connection"""
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class RailwayDB:
    def __init__(self):
        try:
            # Railway provides DATABASE_URL environment variable
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                self.conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
                logger.info("Connected to Railway PostgreSQL database")
            else:
                self.conn = None
                logger.warning("No DATABASE_URL found - using mock database")
        except Exception as e:
            self.conn = None
            logger.error(f"Database connection failed: {e}")
    
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