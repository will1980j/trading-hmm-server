"""
Query Railway database directly for MFE_UPDATE events
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get Railway DATABASE_URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    print("Make sure .env file is loaded")
    exit(1)

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 80)
print("QUERYING RAILWAY DATABASE FOR MFE_UPDATE EVENTS")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Count all event types
    print("\n1. Event type counts:")
    cursor.execute("""
        SELECT event_type, COUNT(*) as count
        FROM automated_signals
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['event_type']}: {row['count']}")
    
    # 2. Check for MFE_UPDATE events specifically
    print("\n2. MFE_UPDATE event details:")
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
    """)
    
    result = cursor.fetchone()
    mfe_count = result['total']
    print(f"  Total MFE_UPDATE events: {mfe_count}")
    
    if mfe_count == 0:
        print("\n  ⚠️  NO MFE_UPDATE EVENTS FOUND!")
        print("  This means the TradingView indicator is NOT sending MFE_UPDATE webhooks.")
        print("  The indicator should send MFE_UPDATE every 60 seconds for active trades.")
    else:
        # Show recent MFE_UPDATE events
        print("\n3. Recent MFE_UPDATE events:")
        cursor.execute("""
            SELECT trade_id, be_mfe, no_be_mfe, current_price, timestamp
            FROM automated_signals
            WHERE event_type = 'MFE_UPDATE'
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"  {row['timestamp']} | {row['trade_id']}")
            print(f"    BE MFE: {row['be_mfe']}, No BE MFE: {row['no_be_mfe']}, Price: {row['current_price']}")
    
    # 4. Check active trades (ENTRY without EXIT)
    print("\n4. Active trades (ENTRY without EXIT):")
    cursor.execute("""
        SELECT trade_id, direction, entry_price, timestamp
        FROM automated_signals
        WHERE event_type = 'ENTRY'
          AND NOT EXISTS (
              SELECT 1 FROM automated_signals ex
              WHERE ex.trade_id = automated_signals.trade_id
                AND ex.event_type LIKE 'EXIT_%'
          )
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['trade_id']}")
        print(f"    Direction: {row['direction']}, Entry: {row['entry_price']}, Time: {row['timestamp']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    if mfe_count == 0:
        print("❌ NO MFE_UPDATE EVENTS IN DATABASE")
        print("\nThe TradingView indicator is NOT sending MFE_UPDATE webhooks.")
        print("This is why MFE values are 0.00 on the dashboard.")
        print("\nTO FIX:")
        print("1. Check TradingView indicator is running on a chart")
        print("2. Verify the indicator sends MFE_UPDATE webhooks every 60 seconds")
        print("3. Check the webhook URL in the indicator matches the Railway URL")
    else:
        print("✅ MFE_UPDATE EVENTS EXIST IN DATABASE")
        print("\nIf dashboard still shows 0.00, the deployment may not be complete.")
        print("Wait 2-3 minutes and refresh the dashboard.")
    print("=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nMake sure DATABASE_URL in .env points to Railway database")
