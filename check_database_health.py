"""
Check Railway database health and transaction status
"""
import os
import psycopg2
from psycopg2 import extensions

def check_database():
    """Check database connection and transaction status"""
    print("🔍 Checking Railway Database Health...")
    print("=" * 60)
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ No DATABASE_URL environment variable found")
        print("💡 Make sure you're running this with Railway environment")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        print("✅ Database connection successful")
        
        # Check transaction status
        status = conn.get_transaction_status()
        status_names = {
            extensions.TRANSACTION_STATUS_IDLE: "IDLE (✅ Good)",
            extensions.TRANSACTION_STATUS_ACTIVE: "ACTIVE (⚠️ Query running)",
            extensions.TRANSACTION_STATUS_INTRANS: "IN TRANSACTION (⚠️ Open transaction)",
            extensions.TRANSACTION_STATUS_INERROR: "IN ERROR (❌ Aborted transaction)",
            extensions.TRANSACTION_STATUS_UNKNOWN: "UNKNOWN (❓ Unknown state)"
        }
        
        print(f"📊 Transaction Status: {status_names.get(status, 'UNKNOWN')}")
        
        # Try a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Test query successful: {result}")
        
        # Check live_signals table
        cursor.execute("SELECT COUNT(*) FROM live_signals")
        count = cursor.fetchone()[0]
        print(f"📊 Live signals in database: {count}")
        
        # Check recent signals
        cursor.execute("""
            SELECT bias, timestamp 
            FROM live_signals 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent = cursor.fetchall()
        
        if recent:
            print(f"\n📈 Recent signals:")
            for signal in recent:
                print(f"   {signal[0]} at {signal[1]}")
        else:
            print("\n⚠️ No signals in database yet")
        
        # Clean up
        conn.rollback()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database is healthy!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print("💡 Check if DATABASE_URL is correct")
        return False
        
    except psycopg2.InternalError as e:
        print(f"❌ Transaction error: {e}")
        print("💡 Database has aborted transaction - needs rollback")
        try:
            conn.rollback()
            print("✅ Rolled back aborted transaction")
        except:
            pass
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    check_database()
