import requests
import json

print("=== TESTING NEW STATS ENDPOINT ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Press Enter after deployment...")
input()

print("\n1. Testing NEW stats-v2 endpoint...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/stats-v2', timeout=10)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print(f"   Total signals: {stats.get('total_signals', 0)}")
        print(f"   Active: {stats.get('active_count', 0)}")
        print(f"   Completed: {stats.get('completed_count', 0)}")
        
        if stats.get('total_signals', 0) > 0:
            print("\n   ✓✓✓ NEW ENDPOINT WORKS! ✓✓✓")
        else:
            print("\n   ✗ Still showing 0")
    else:
        print(f"   Error: {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. Testing OLD stats endpoint (should also work now)...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print(f"   Total signals: {stats.get('total_signals', 0)}")
        print(f"   Active: {stats.get('active_count', 0)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. Debug endpoint for comparison...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/debug', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ENTRY records: {data.get('entry_count', 0)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n✓ If stats-v2 works, update the dashboard to use /api/automated-signals/stats-v2")
