import requests
import json

print("=" * 70)
print("CALENDAR DIAGNOSIS - Checking Production API")
print("=" * 70)

# Test the production API
url = 'https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data'
print(f"\n1. Testing API: {url}")

try:
    r = requests.get(url, timeout=10)
    print(f"   Status Code: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        
        print(f"\n2. API Response Structure:")
        print(f"   - success: {data.get('success')}")
        print(f"   - message: {data.get('message')}")
        print(f"   - active_trades: {len(data.get('active_trades', []))} trades")
        print(f"   - completed_trades: {len(data.get('completed_trades', []))} trades")
        
        # Check if we have any trades
        all_trades = data.get('active_trades', []) + data.get('completed_trades', [])
        
        if all_trades:
            print(f"\n3. Checking First Trade for 'date' field:")
            first_trade = all_trades[0]
            print(f"   Trade ID: {first_trade.get('trade_id', 'N/A')}")
            print(f"   Has 'date' field: {'date' in first_trade}")
            print(f"   Has 'created_at' field: {'created_at' in first_trade}")
            print(f"   Has 'timestamp' field: {'timestamp' in first_trade}")
            
            if 'date' in first_trade:
                print(f"   ✅ date value: {first_trade['date']}")
            else:
                print(f"   ❌ date field MISSING")
                print(f"   created_at: {first_trade.get('created_at', 'N/A')}")
                print(f"   timestamp: {first_trade.get('timestamp', 'N/A')}")
            
            print(f"\n4. All fields in first trade:")
            for key in sorted(first_trade.keys()):
                value = first_trade[key]
                if isinstance(value, (dict, list)):
                    print(f"   - {key}: {type(value).__name__}")
                else:
                    print(f"   - {key}: {value}")
        else:
            print(f"\n3. ❌ NO TRADES FOUND")
            print(f"   This is why calendar is empty!")
            print(f"   Calendar needs trades with 'date' field to display")
            
        # Check debug info
        if 'debug_info' in data:
            print(f"\n5. Debug Info:")
            for key, value in data['debug_info'].items():
                print(f"   - {key}: {value}")
                
    else:
        print(f"   ❌ API returned error status: {r.status_code}")
        print(f"   Response: {r.text[:500]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
