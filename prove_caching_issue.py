import requests
import json

print("=== PROVING THE CACHING/ROUTING ISSUE ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Press Enter after deployment...")
input()

print("\nRunning debug endpoint (which now includes stats queries)...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/debug', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"\nDebug endpoint results:")
        print(f"  Total in DB: {data.get('total_in_db', 0)}")
        print(f"  ENTRY count: {data.get('entry_count', 0)}")
        print(f"  EXIT count: {data.get('exit_count', 0)}")
        print(f"  Message: {data.get('message', '')}")
except Exception as e:
    print(f"Error: {e}")

print("\nNow checking stats endpoint...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print(f"\nStats endpoint results:")
        print(f"  Total signals: {stats.get('total_signals', 0)}")
        print(f"  Active count: {stats.get('active_count', 0)}")
        print(f"  Completed count: {stats.get('completed_count', 0)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
print("""
If debug shows ENTRY count > 0 but stats shows 0:
- The stats endpoint is being cached
- OR there are multiple Railway instances
- OR the stats endpoint is hitting a different route

Solution: Add cache-busting headers to stats endpoint
""")
