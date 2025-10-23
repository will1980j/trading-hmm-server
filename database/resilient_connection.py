"""
Production-Grade Resilient Database Connection Manager
Handles all PostgreSQL errors with automatic recovery, connection pooling, and health monitoring
"""
import psycopg2
from psycopg2 import pool, extensions, OperationalError, InterfaceError, DatabaseError
from psycopg2.extras import RealDictCursor
import logging
import time
import os
from threading import Lock
from functools import wraps

logger = logging.getLogger(__name__)

class ResilientDatabaseConnection:
    """
    Self-healing database connection with automatic error recovery
    Features:
    - Connection pooling with automatic cleanup
    - Automatic reconnection on all error types
    - Transaction state management
    - Query retry with exponential backoff
    - Health monitoring and metrics
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.database_url = os.getenv('DATABASE_URL')
        self.pool = None
        self.conn = None
        self._connection_lock = Lock()
        
        # Resilience configuration
        self.max_retries = 3
        self.retry_delay = 0.5
        self.max_retry_delay = 5.0
        self.pool_min_conn = 2
        self.pool_max_conn = 20
        
        # Health metrics
        self.metrics = {
            'total_queries': 0,
            'failed_queries': 0,
            'reconnections': 0,
            'transaction_rollbacks': 0,
            'pool_resets': 0
        }
        
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool with error handling"""
        try:
            if self.pool:
                self.pool.closeall()
            
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                self.pool_min_conn,
                self.pool_max_conn,
                self.database_url,
                cursor_factory=RealDictCursor
            )
            
            self.conn = self.pool.getconn()
            self.conn.set_session(autocommit=False)
            logger.info("✅ Database pool initialized")
            
        except Exception as e:
            logger.error(f"❌ Pool initialization failed: {e}")
            self.pool = None
            self.conn = None
            raise
    
    def _get_connection(self):
        """Get connection from pool with automatic recovery"""
        with self._connection_lock:
            if not self.pool:
                self._initialize_pool()
            
            if not self.conn:
                try:
                    self.conn = self.pool.getconn()
                    self.conn.set_session(autocommit=False)
                except Exception as e:
                    logger.error(f"❌ Failed to get connection: {e}")
                    self._initialize_pool()
                    self.conn = self.pool.getconn()
            
            return self.conn
    
    def _check_and_fix_transaction_state(self):
        """Check and fix transaction state before query execution"""
        if not self.conn:
            return
        
        try:
            status = self.conn.get_transaction_status()
            
            if status == extensions.TRANSACTION_STATUS_INERROR:
                logger.warning("⚠️ Aborted transaction detected - rolling back")
                self.conn.rollback()
                self.metrics['transaction_rollbacks'] += 1
                
            elif status == extensions.TRANSACTION_STATUS_INTRANS:
                logger.warning("⚠️ Open transaction detected - committing")
                self.conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Transaction state check failed: {e}")
            try:
                self.conn.rollback()
            except:
                pass
    
    def _reconnect(self):
        """Force reconnection with pool reset"""
        logger.warning("🔄 Forcing reconnection...")
        
        with self._connection_lock:
            try:
                if self.conn:
                    try:
                        self.pool.putconn(self.conn)
                    except:
                        pass
                    self.conn = None
                
                if self.pool:
                    try:
                        self.pool.closeall()
                    except:
                        pass
                    self.pool = None
                
                self._initialize_pool()
                self.metrics['reconnections'] += 1
                logger.info("✅ Reconnection successful")
                
            except Exception as e:
                logger.error(f"❌ Reconnection failed: {e}")
                raise
    
    def execute_with_retry(self, query, params=None, fetch=True):
        """
        Execute query with automatic retry and error recovery
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results or None
        """
        self.metrics['total_queries'] += 1
        retry_delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                # Ensure connection is healthy
                conn = self._get_connection()
                self._check_and_fix_transaction_state()
                
                # Execute query
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Fetch results if requested
                if fetch:
                    if query.strip().upper().startswith('SELECT'):
                        return cursor.fetchall()
                    elif query.strip().upper().startswith('INSERT') and 'RETURNING' in query.upper():
                        return cursor.fetchone()
                
                return None
                
            except (OperationalError, InterfaceError) as e:
                logger.error(f"❌ Connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                self.metrics['failed_queries'] += 1
                
                if attempt < self.max_retries - 1:
                    self._reconnect()
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                else:
                    raise
                    
            except DatabaseError as e:
                logger.error(f"❌ Database error: {e}")
                self.metrics['failed_queries'] += 1
                
                try:
                    self.conn.rollback()
                    self.metrics['transaction_rollbacks'] += 1
                except:
                    pass
                
                if attempt < self.max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                self.metrics['failed_queries'] += 1
                
                try:
                    self.conn.rollback()
                except:
                    pass
                
                raise
        
        return None
    
    def commit(self):
        """Commit transaction with retry"""
        for attempt in range(self.max_retries):
            try:
                if self.conn:
                    self.conn.commit()
                return
            except Exception as e:
                logger.error(f"❌ Commit failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    self._reconnect()
                else:
                    raise
    
    def rollback(self):
        """Rollback transaction safely"""
        try:
            if self.conn:
                self.conn.rollback()
                self.metrics['transaction_rollbacks'] += 1
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            self._reconnect()
    
    def get_health_status(self):
        """Get connection health status and metrics"""
        try:
            result = self.execute_with_retry("SELECT 1", fetch=True)
            is_healthy = result is not None
            
            return {
                'healthy': is_healthy,
                'metrics': self.metrics.copy(),
                'pool_size': self.pool_max_conn if self.pool else 0,
                'success_rate': (1 - (self.metrics['failed_queries'] / max(self.metrics['total_queries'], 1))) * 100
            }
        except:
            return {
                'healthy': False,
                'metrics': self.metrics.copy(),
                'pool_size': 0,
                'success_rate': 0
            }
    
    def close(self):
        """Close all connections"""
        with self._connection_lock:
            if self.conn:
                try:
                    self.pool.putconn(self.conn)
                except:
                    pass
                self.conn = None
            
            if self.pool:
                try:
                    self.pool.closeall()
                except:
                    pass
                self.pool = None


def resilient_db_operation(func):
    """
    Decorator for database operations with automatic error handling
    
    Usage:
        @resilient_db_operation
        def my_function(db):
            cursor = db.conn.cursor()
            cursor.execute("SELECT ...")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = ResilientDatabaseConnection()
        
        for attempt in range(db.max_retries):
            try:
                return func(*args, **kwargs)
            except (OperationalError, InterfaceError, DatabaseError) as e:
                logger.error(f"❌ {func.__name__} failed (attempt {attempt + 1}): {e}")
                
                if attempt < db.max_retries - 1:
                    db.rollback()
                    time.sleep(db.retry_delay * (attempt + 1))
                else:
                    raise
            except Exception as e:
                logger.error(f"❌ {func.__name__} unexpected error: {e}")
                db.rollback()
                raise
        
        return None
    
    return wrapper


# Global singleton instance
_global_db = None

def get_resilient_db():
    """Get global resilient database instance"""
    global _global_db
    if _global_db is None:
        _global_db = ResilientDatabaseConnection()
    return _global_db
