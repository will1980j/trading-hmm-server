import requests
import json
import time

print("=== TESTING CACHE-BUSTING FIX ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Press Enter after deployment...")
input()

print("\n1. Testing stats endpoint with cache-busting...")
for i in range(3):
    print(f"\n   Attempt {i+1}:")
    try:
        # Add cache-busting query parameter
        response = requests.get(
            f'{base_url}/api/automated-signals/stats?_={int(time.time()*1000)}',
            headers={'Cache-Control': 'no-cache'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"   Total signals: {stats.get('total_signals', 0)}")
            print(f"   Active: {stats.get('active_count', 0)}")
            
            if stats.get('total_signals', 0) > 0:
                print("\n   ✓✓✓ CACHE-BUSTING WORKED! ✓✓✓")
                break
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)

print("\n2. Comparing with debug endpoint...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/debug', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Debug shows: {data.get('entry_count', 0)} ENTRY records")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. If stats still shows 0:")
print("   - Railway might be running multiple instances")
print("   - Try restarting the Railway service")
print("   - Or wait a few minutes for all instances to update")
