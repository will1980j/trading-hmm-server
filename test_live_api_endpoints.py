import requests
import json

base_url = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("TESTING LIVE API ENDPOINTS")
print("=" * 80)

endpoints = [
    "/api/automated-signals/dashboard-data",
    "/api/automated-signals/stats",
    "/api/automated-signals/active",
    "/api/automated-signals/completed",
    "/api/automated-signals/hourly-distribution",
    "/api/automated-signals/mfe-distribution"
]

for endpoint in endpoints:
    print(f"\n{endpoint}")
    print("-" * 80)
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Keys: {list(data.keys())}")
            if 'stats' in data:
                print(f"Stats: {data['stats']}")
            if 'active_trades' in data:
                print(f"Active Trades: {len(data['active_trades'])}")
            if 'completed_trades' in data:
                print(f"Completed Trades: {len(data['completed_trades'])}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "=" * 80)
