"""
Check if automated signals are in the database
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL not set")
    exit(1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'automated_signals'
        )
    """)
    table_exists = cursor.fetchone()['exists']
    
    if not table_exists:
        print("❌ Table 'automated_signals' does not exist")
        exit(1)
    
    print("✅ Table 'automated_signals' exists")
    
    # Get all signals
    cursor.execute("""
        SELECT * FROM automated_signals 
        ORDER BY timestamp DESC 
        LIMIT 20
    """)
    
    signals = cursor.fetchall()
    
    print(f"\n📊 Found {len(signals)} signals in database:\n")
    
    for signal in signals:
        print(f"ID: {signal['id']}")
        print(f"  Trade ID: {signal['trade_id']}")
        print(f"  Event: {signal['event_type']}")
        print(f"  Direction: {signal.get('direction', 'N/A')}")
        print(f"  Entry: {signal.get('entry_price', 'N/A')}")
        print(f"  Stop Loss: {signal.get('stop_loss', 'N/A')}")
        print(f"  MFE: {signal.get('mfe', 'N/A')}")
        print(f"  Session: {signal.get('session', 'N/A')}")
        print(f"  Timestamp: {signal['timestamp']}")
        print()
    
    cursor.close()
    conn.close()
    
    print("✅ Database check complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
