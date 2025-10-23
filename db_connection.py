"""Database Connection Handler with Auto-Retry and Health Checks"""
import psycopg2
from psycopg2 import pool
import os
import time
import logging

logger = logging.getLogger(__name__)

_connection_pool = None

def get_db_connection():
    """Get database connection with auto-retry"""
    global _connection_pool
    
    if _connection_pool is None:
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL not set")
            
            _connection_pool = pool.SimpleConnectionPool(
                1, 10,
                database_url,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = _connection_pool.getconn()
            if conn:
                return conn
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise
    
    raise Exception("Failed to get database connection")

def release_connection(conn):
    """Release connection back to pool"""
    global _connection_pool
    if _connection_pool and conn:
        _connection_pool.putconn(conn)
