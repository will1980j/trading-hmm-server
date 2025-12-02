"""
Diagnose MFE deployment issue - check if MFE_UPDATE events exist
"""
from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get Railway DATABASE_URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    exit(1)

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 80)
print("MFE DEPLOYMENT DIAGNOSTIC")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Count all event types
    print("\n1. EVENT TYPE COUNTS:")
    cursor.execute("""
        SELECT event_type, COUNT(*) as count
        FROM automated_signals
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    event_counts = {}
    for row in cursor.fetchall():
        event_counts[row['event_type']] = row['count']
        print(f"   {row['event_type']}: {row['count']}")
    
    # 2. Check for MFE_UPDATE events
    mfe_count = event_counts.get('MFE_UPDATE', 0)
    
    print(f"\n2. MFE_UPDATE STATUS:")
    print(f"   Total MFE_UPDATE events: {mfe_count}")
    
    if mfe_count == 0:
        print("\n   ❌ NO MFE_UPDATE EVENTS FOUND!")
        print("   The TradingView indicator is NOT sending MFE_UPDATE webhooks.")
        print("   This is why dashboard shows 0.00 for all MFE values.")
    else:
        print(f"\n   ✅ {mfe_count} MFE_UPDATE events found")
        
        # Show recent MFE_UPDATE events
        print("\n3. RECENT MFE_UPDATE EVENTS:")
        cursor.execute("""
            SELECT trade_id, be_mfe, no_be_mfe, current_price, timestamp
            FROM automated_signals
            WHERE event_type = 'MFE_UPDATE'
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"   {row['timestamp']} | {row['trade_id'][:30]}...")
            print(f"     BE: {row['be_mfe']}, No BE: {row['no_be_mfe']}, Price: {row['current_price']}")
    
    # 3. Check active trades
    print("\n4. ACTIVE TRADES (ENTRY without EXIT):")
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
    
    active_trades = cursor.fetchall()
    print(f"   Total active trades: {len(active_trades)}")
    for row in active_trades:
        print(f"   {row['trade_id'][:30]}... | {row['direction']} @ {row['entry_price']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    
    if mfe_count == 0:
        print("❌ ROOT CAUSE: NO MFE_UPDATE WEBHOOKS")
        print("\nThe TradingView indicator is NOT sending MFE_UPDATE events.")
        print("Without MFE_UPDATE events, the dashboard will always show 0.00.")
        print("\nSOLUTION:")
        print("1. Verify TradingView indicator is running on an active chart")
        print("2. Check indicator sends MFE_UPDATE webhook every 60 seconds")
        print("3. Verify webhook URL matches Railway deployment")
        print("4. Check TradingView alert log for MFE_UPDATE alerts")
    else:
        print("✅ MFE_UPDATE EVENTS EXIST")
        print("\nIf dashboard still shows 0.00:")
        print("1. Railway deployment may not be complete (wait 2-3 minutes)")
        print("2. Browser cache may be stale (hard refresh: Ctrl+Shift+R)")
        print("3. Check Railway logs for deployment errors")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
