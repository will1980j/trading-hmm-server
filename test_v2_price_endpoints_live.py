"""
Test V2 Price Endpoints on Production
"""
import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("🧪 TESTING V2 PRICE ENDPOINTS")
print("=" * 60)

# Test 1: Current Price
print("\n1. Testing /api/v2/price/current")
try:
    response = requests.get(f"{BASE_URL}/api/v2/price/current", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS: {data}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 2: Price Stream
print("\n2. Testing /api/v2/price/stream?limit=1")
try:
    response = requests.get(f"{BASE_URL}/api/v2/price/stream?limit=1", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS: {data}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 3: V2 Stats
print("\n3. Testing /api/v2/stats")
try:
    response = requests.get(f"{BASE_URL}/api/v2/stats", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS: {data}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 4: Check if realtime_prices table has data
print("\n4. Testing /api/realtime-price (webhook endpoint)")
print("   This should be POST only, GET should fail")
try:
    response = requests.get(f"{BASE_URL}/api/realtime-price", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {str(e)}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("If /api/v2/price/current returns 404:")
print("  → Endpoint not deployed to Railway")
print("  → Need to commit and push web_server.py")
print("If /api/v2/price/current returns 500:")
print("  → Endpoint exists but has error")
print("  → Check Railway logs for details")
print("If /api/v2/price/current returns empty data:")
print("  → No price data in realtime_prices table")
print("  → TradingView price streamer not sending data")
