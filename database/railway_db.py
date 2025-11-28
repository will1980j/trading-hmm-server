"""Railway PostgreSQL database connection - Railway-only, no fallbacks"""
from os import environ
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import extensions

# Get Railway DATABASE_URL - fail immediately if missing
DATABASE_URL = environ.get("DATABASE_URL")

# TEMPORARY DEBUG: Print DATABASE_URL with masked password
if DATABASE_URL:
    import re
    masked_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:*****@', DATABASE_URL)
    print("### RUNTIME DATABASE_URL:", masked_url)
else:
    print("### RUNTIME DATABASE_URL: None")

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL is missing — Railway DB cannot be reached.")

# Connect to Railway PostgreSQL with SSL
conn = psycopg2.connect(DATABASE_URL, sslmode='require', cursor_factory=RealDictCursor)
conn.set_isolation_level(extensions.ISOLATION_LEVEL_READ_COMMITTED)
conn.rollback()

class RailwayDB:
    """Railway PostgreSQL database connection wrapper"""
    
    def __init__(self, use_pool=True):
        """Initialize with Railway connection only"""
        self.conn = conn
    
    def close(self):
        """Close connection"""
        try:
            if self.conn:
                self.conn.close()
        except:
            pass
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
    
    def ensure_clean_transaction(self):
        """Ensure transaction is in clean state"""
        try:
            status = self.conn.get_transaction_status()
            if status == extensions.TRANSACTION_STATUS_INERROR:
                self.conn.rollback()
        except:
            pass
        return True
