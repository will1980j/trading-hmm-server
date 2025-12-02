"""
Check if MFE updates are working on live deployment
"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("CHECKING LIVE MFE UPDATES")
print("=" * 80)

# 1. Check dashboard-data endpoint
print("\n1. Fetching dashboard-data...")
try:
    r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
    data = r.json()
    
    print(f"Status: {r.status_code}")
    print(f"Active trades count: {len(data.get('active_trades', []))}")
    
    if data.get('active_trades'):
        print("\nFirst active trade:")
        trade = data['active_trades'][0]
        print(f"  Trade ID: {trade.get('trade_id')}")
        print(f"  Direction: {trade.get('direction')}")
        print(f"  Entry Price: {trade.get('entry_price')}")
        print(f"  BE MFE: {trade.get('be_mfe')}")
        print(f"  No BE MFE: {trade.get('no_be_mfe')}")
        print(f"  Current Price: {trade.get('current_price')}")
        print(f"  Status: {trade.get('status')}")
        
        # Check if MFE values are non-zero
        if trade.get('be_mfe', 0) == 0 and trade.get('no_be_mfe', 0) == 0:
            print("\n⚠️  WARNING: MFE values are still 0.00!")
            print("   This means the fix hasn't been deployed yet or MFE_UPDATE events haven't arrived.")
        else:
            print("\n✅ MFE values are non-zero - fix is working!")
            
except Exception as e:
    print(f"Error: {e}")

# 2. Check if there are any MFE_UPDATE events in the database
print("\n" + "=" * 80)
print("2. Checking for MFE_UPDATE events...")
print("=" * 80)

try:
    # We need to query the database directly
    import os
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Count MFE_UPDATE events
    cursor.execute("""
        SELECT 
            COUNT(*) as total_mfe_updates,
            COUNT(DISTINCT trade_id) as trades_with_mfe,
            MAX(timestamp) as latest_mfe_update
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
    """)
    
    result = cursor.fetchone()
    print(f"Total MFE_UPDATE events: {result['total_mfe_updates']}")
    print(f"Trades with MFE updates: {result['trades_with_mfe']}")
    print(f"Latest MFE update: {result['latest_mfe_update']}")
    
    if result['total_mfe_updates'] == 0:
        print("\n⚠️  NO MFE_UPDATE EVENTS FOUND!")
        print("   The indicator may not be sending MFE_UPDATE webhooks.")
        print("   Check TradingView indicator is running and sending updates every 60 seconds.")
    
    # Get sample MFE_UPDATE data
    cursor.execute("""
        SELECT trade_id, be_mfe, no_be_mfe, current_price, timestamp
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    
    print("\nRecent MFE_UPDATE events:")
    for row in cursor.fetchall():
        print(f"  {row['trade_id']}: BE={row['be_mfe']}, No BE={row['no_be_mfe']}, Price={row['current_price']}, Time={row['timestamp']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Database check error: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
