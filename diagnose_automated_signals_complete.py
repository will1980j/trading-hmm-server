"""
Complete diagnostic for automated signals dashboard issues
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

DATABASE_URL = os.environ.get('DATABASE_URL')
BASE_URL = 'https://web-production-cd33.up.railway.app'

print("=" * 80)
print("AUTOMATED SIGNALS DASHBOARD DIAGNOSTIC")
print("=" * 80)

# 1. Check database table existence
print("\n1. DATABASE TABLE CHECK")
print("-" * 80)
try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    # Check if automated_signals table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'automated_signals'
        );
    """)
    table_exists = cursor.fetchone()['exists']
    print(f"✓ Table 'automated_signals' exists: {table_exists}")
    
    if table_exists:
        # Get table schema
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"\n  Table Schema ({len(columns)} columns):")
        for col in columns:
            print(f"    - {col['column_name']}: {col['data_type']}")
        
        # Count records
        cursor.execute("SELECT COUNT(*) as count FROM automated_signals;")
        total = cursor.fetchone()['count']
        print(f"\n  Total records: {total}")
        
        if total > 0:
            # Count by event_type
            cursor.execute("""
                SELECT event_type, COUNT(*) as count 
                FROM automated_signals 
                GROUP BY event_type 
                ORDER BY count DESC;
            """)
            event_types = cursor.fetchall()
            print(f"\n  Records by event_type:")
            for et in event_types:
                print(f"    - {et['event_type']}: {et['count']}")
            
            # Recent records
            cursor.execute("""
                SELECT id, trade_id, event_type, direction, timestamp
                FROM automated_signals
                ORDER BY timestamp DESC
                LIMIT 5;
            """)
            recent = cursor.fetchall()
            print(f"\n  Recent records (last 5):")
            for rec in recent:
                print(f"    - ID {rec['id']}: {rec['event_type']} | {rec['direction']} | {rec['timestamp']}")
    else:
        print("\n  ❌ TABLE DOES NOT EXIST!")
        print("  This is why the dashboard shows no data.")
        print("\n  Solution: Create the automated_signals table")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"  ❌ Database error: {e}")

# 2. Check API endpoints
print("\n\n2. API ENDPOINT CHECK")
print("-" * 80)

endpoints = [
    '/api/automated-signals/dashboard-data',
    '/api/automated-signals/stats',
    '/api/automated-signals/active',
    '/api/automated-signals/completed'
]

for endpoint in endpoints:
    try:
        response = requests.get(f'{BASE_URL}{endpoint}', timeout=10)
        print(f"\n  {endpoint}")
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'signals' in data:
                print(f"    Signals: {len(data['signals'])}")
            if 'active_trades' in data:
                print(f"    Active trades: {len(data['active_trades'])}")
            if 'completed_trades' in data:
                print(f"    Completed trades: {len(data['completed_trades'])}")
            if 'stats' in data:
                print(f"    Stats: {data['stats']}")
        else:
            print(f"    Error: {response.text[:100]}")
    except Exception as e:
        print(f"    ❌ Exception: {e}")

# 3. Check WebSocket endpoint
print("\n\n3. WEBSOCKET CHECK")
print("-" * 80)
print(f"  WebSocket URL: wss://{BASE_URL.replace('https://', '')}/socket.io/")
print(f"  Error reported: 'Invalid frame header'")
print(f"\n  Possible causes:")
print(f"    1. SocketIO version mismatch between client and server")
print(f"    2. CORS/proxy issues with WebSocket upgrade")
print(f"    3. Railway platform WebSocket configuration")
print(f"\n  Solution: Check SocketIO initialization in web_server.py")

# 4. Summary
print("\n\n4. SUMMARY & RECOMMENDATIONS")
print("=" * 80)

if not table_exists:
    print("\n❌ CRITICAL ISSUE: automated_signals table does not exist")
    print("\nRECOMMENDATIONS:")
    print("  1. Create the automated_signals table using the schema")
    print("  2. Deploy the table creation to Railway")
    print("  3. Test webhook to populate data")
else:
    if total == 0:
        print("\n⚠️  WARNING: automated_signals table exists but is empty")
        print("\nRECOMMENDATIONS:")
        print("  1. Check if TradingView webhooks are configured")
        print("  2. Test webhook endpoint: POST /api/automated-signals")
        print("  3. Verify webhook is receiving and storing data")
    else:
        print("\n✓ Database has data")
        print("\nRECOMMENDATIONS:")
        print("  1. Check API query logic in automated_signals_api.py")
        print("  2. Verify data format matches frontend expectations")
        print("  3. Check browser console for JavaScript errors")

print("\n⚠️  WebSocket issue needs separate investigation")
print("  - Check SocketIO version compatibility")
print("  - Review Railway WebSocket configuration")
print("  - Test with simple WebSocket connection")

print("\n" + "=" * 80)
