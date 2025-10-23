"""
Automatic Database Error Handler
Decorator that automatically fixes common database errors
"""
import logging
from functools import wraps
from psycopg2 import extensions, OperationalError, InterfaceError

logger = logging.getLogger(__name__)

def auto_fix_db_errors(func):
    """
    Decorator that automatically handles database transaction errors
    
    Usage:
        @auto_fix_db_errors
        def my_db_function(self):
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT ...")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get db instance (assumes first arg is self with db attribute)
        db = None
        if args and hasattr(args[0], 'db'):
            db = args[0].db
        
        if not db or not hasattr(db, 'conn') or not db.conn:
            logger.warning(f"{func.__name__}: No database connection")
            return func(*args, **kwargs)
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Check transaction status before executing
                status = db.conn.get_transaction_status()
                
                if status == extensions.TRANSACTION_STATUS_INERROR:
                    logger.warning(f"{func.__name__}: Auto-fixing aborted transaction")
                    db.conn.rollback()
                elif status == extensions.TRANSACTION_STATUS_INTRANS:
                    logger.warning(f"{func.__name__}: Auto-committing open transaction")
                    db.conn.commit()
                
                # Execute the function
                return func(*args, **kwargs)
                
            except (OperationalError, InterfaceError) as e:
                logger.error(f"{func.__name__}: Connection error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Try to rollback and retry
                    try:
                        db.conn.rollback()
                    except:
                        pass
                else:
                    # Last attempt failed
                    logger.error(f"{func.__name__}: All retry attempts failed")
                    raise
                    
            except Exception as e:
                # For other errors, try rollback once
                logger.error(f"{func.__name__}: Error: {e}")
                try:
                    db.conn.rollback()
                except:
                    pass
                raise
        
        return None
    
    return wrapper
