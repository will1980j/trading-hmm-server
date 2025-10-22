"""Railway PostgreSQL database connection with connection pooling"""
import logging
import os
import psycopg2
from psycopg2 import pool, extensions
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = None

def get_connection_pool():
    """Get or create the connection pool"""
    global _connection_pool
    
    if _connection_pool is None:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            try:
                _connection_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,  # Max 10 connections
                    dsn=database_url
                )
                logger.info("✅ Connection pool created (1-10 connections)")
            except Exception as e:
                logger.error(f"❌ Failed to create connection pool: {e}")
                _connection_pool = None
    
    return _connection_pool

class RailwayDB:
    def __init__(self, use_pool=True):
        """
        Initialize database connection
        
        Args:
            use_pool: If True, use connection pooling (recommended)
        """
        self.conn = None
        self.use_pool = use_pool
        self._pool_connection = None
        
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logger.warning("No DATABASE_URL found - using mock database")
                return
            
            if use_pool:
                # Get connection from pool
                pool_obj = get_connection_pool()
                if pool_obj:
                    try:
                        self.conn = pool_obj.getconn()
                        self._pool_connection = True
                        
                        # Configure connection
                        self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_READ_COMMITTED)
                        
                        # Always start clean
                        self.conn.rollback()
                        logger.info("✅ Got connection from pool")
                    except Exception as e:
                        logger.error(f"❌ Failed to get pooled connection: {e}")
                        # Fall back to direct connection
                        use_pool = False
            
            if not use_pool or not self.conn:
                # Direct connection (fallback)
                self.conn = psycopg2.connect(
                    database_url, 
                    cursor_factory=RealDictCursor
                )
                self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_READ_COMMITTED)
                self._pool_connection = False
                
                # Always start clean
                self.conn.rollback()
                logger.info("✅ Direct database connection established")
                
        except Exception as e:
            self.conn = None
            logger.error(f"❌ Database connection failed: {e}")
    
    def close(self):
        """Close connection (returns to pool if pooled)"""
        if self.conn:
            try:
                if self._pool_connection:
                    # Return to pool
                    pool_obj = get_connection_pool()
                    if pool_obj:
                        pool_obj.putconn(self.conn)
                        logger.info("🔄 Connection returned to pool")
                else:
                    # Close direct connection
                    self.conn.close()
                    logger.info("🔒 Direct connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.conn = None
    
    def __del__(self):
        """Destructor - ensure connection is returned/closed"""
        self.close()
    
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