"""
Test the DEPLOYED calendar API to see what it's actually returning
"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("Testing DEPLOYED calendar API...")

try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/daily-calendar", timeout=10)
    print(f"Status: {resp.status_code}")
    
    data = resp.json()
    print(f"\nResponse structure:")
    print(json.dumps(data, indent=2)[:500])
    
    if data.get('success'):
        daily_data = data.get('daily_data', {})
        print(f"\n✅ Got {len(daily_data)} days of data")
        
        if len(daily_data) > 0:
            # Show a sample day
            sample_date = list(daily_data.keys())[0]
            print(f"\nSample day ({sample_date}):")
            print(json.dumps(daily_data[sample_date], indent=2))
        else:
            print("\n🚨 NO DATA RETURNED - This is why badges aren't showing!")
    else:
        print(f"\n❌ API returned error: {data}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
