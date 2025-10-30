"""
Test Signal Lab calendar data via Railway API
"""

import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("SIGNAL LAB CALENDAR DATA TEST")
print("=" * 80)

# Test the API endpoint that the calendar uses
try:
    response = requests.get(f"{BASE_URL}/api/signal-lab-trades")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API Response: {response.status_code}")
        print(f"📊 Total trades returned: {len(data)}")
        
        if len(data) > 0:
            print(f"\n🔍 Sample trade data:")
            sample = data[0]
            print(f"  Keys: {list(sample.keys())}")
            print(f"  Date: {sample.get('date')}")
            print(f"  Session: {sample.get('session')}")
            print(f"  Bias: {sample.get('bias')}")
            print(f"  MFE: {sample.get('mfe')}")
            
            # Check date formats
            dates = set([t.get('date') for t in data if t.get('date')])
            print(f"\n📅 Unique dates found: {len(dates)}")
            print(f"  Sample dates: {list(dates)[:5]}")
        else:
            print("\n❌ No trades returned from API!")
    else:
        print(f"\n❌ API Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
