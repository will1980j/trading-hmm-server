import requests
import json
from datetime import datetime

print("=" * 80)
print("TESTING DASHBOARD DATA ENDPOINT")
print("=" * 80)

# Test the dashboard-data endpoint
url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"
print(f"\nFetching: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            print("\n✅ SUCCESS - Dashboard data retrieved")
            
            # Check active trades
            active_trades = data.get('active_trades', [])
            print(f"\nActive Trades: {len(active_trades)}")
            
            if active_trades:
                print("\nMost Recent Active Trade:")
                latest = active_trades[0]
                print(f"  Trade ID: {latest.get('trade_id')}")
                print(f"  Direction: {latest.get('direction')}")
                print(f"  Entry: {latest.get('entry_price')}")
                print(f"  Signal Time: {latest.get('signal_time')}")
                print(f"  MFE (BE): {latest.get('be_mfe')}")
                print(f"  MFE (No BE): {latest.get('no_be_mfe')}")
            
            # Check completed trades
            completed_trades = data.get('completed_trades', [])
            print(f"\nCompleted Trades: {len(completed_trades)}")
            
            # Check stats
            stats = data.get('stats', {})
            print(f"\nStats:")
            print(f"  Total Signals: {stats.get('total_signals')}")
            print(f"  Active: {stats.get('active_count')}")
            print(f"  Completed: {stats.get('completed_count')}")
            print(f"  Avg MFE: {stats.get('avg_mfe')}")
            
        else:
            print(f"\n❌ ERROR: {data.get('error')}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

# Also test stats-live endpoint
print("\n" + "=" * 80)
print("TESTING STATS-LIVE ENDPOINT")
print("=" * 80)

url2 = "https://web-production-cd33.up.railway.app/api/automated-signals/stats-live"
print(f"\nFetching: {url2}")

try:
    response2 = requests.get(url2)
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"\nStats: {json.dumps(data2.get('stats', {}), indent=2)}")
    else:
        print(f"Error: {response2.text[:500]}")
        
except Exception as e:
    print(f"Exception: {e}")
