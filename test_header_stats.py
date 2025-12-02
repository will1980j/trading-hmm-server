"""
Test the header stats to see why they're showing zeros
"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("Testing header stats endpoints...")

# Test dashboard-data endpoint
print("\n1. Testing /api/automated-signals/dashboard-data")
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=10)
    data = resp.json()
    
    stats = data.get('stats', {})
    active = data.get('active_trades', [])
    completed = data.get('completed_trades', [])
    
    print(f"  Active trades: {len(active)}")
    print(f"  Completed trades: {len(completed)}")
    print(f"  Stats object: {stats}")
    
    if not stats:
        print("  🚨 NO STATS OBJECT RETURNED!")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test stats-live endpoint
print("\n2. Testing /api/automated-signals/stats-live")
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/stats-live", timeout=10)
    data = resp.json()
    
    print(f"  Response: {data}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")
