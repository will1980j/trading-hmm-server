import requests
import json

print("=== FINAL STATS TEST ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Press Enter after deployment...")
input()

print("\n1. Debug endpoint (baseline):")
try:
    response = requests.get(f'{base_url}/api/automated-signals/debug', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Total in DB: {data.get('total_in_db', 0)}")
        
        # Count event types
        records = data.get('last_10_records', [])
        event_types = {}
        for r in records:
            et = r.get('event_type')
            event_types[et] = event_types.get(et, 0) + 1
        print(f"   Event types in last 10: {event_types}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. Stats endpoint (should match debug):")
try:
    response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        stats = data.get('stats', {})
        if stats.get('total_signals', 0) > 0:
            print("\n   ✓✓✓ STATS WORKING! ✓✓✓")
        else:
            error = data.get('error', 'No error message')
            print(f"\n   ✗ Still showing 0 signals")
            print(f"   Error field: {error}")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. If stats still show 0, the issue is:")
print("   - Exception being caught and returning empty stats")
print("   - Check Railway logs for the actual error")
print("   - Look for 'Stats error:' in the logs")
