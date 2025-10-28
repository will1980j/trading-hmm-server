"""
Test Polygon.io API - Following Official Documentation
https://polygon.io/docs/rest/quickstart
"""
import requests
import json

API_KEY = "_azuCKXmKg9r1442lnX90Sx1zYLeu_hZ"

print("🧪 TESTING POLYGON.IO API")
print("=" * 60)

# Test 1: Get NASDAQ-100 Index (NDX)
print("\n1. Testing NASDAQ-100 Index (I:NDX)")
url = f"https://api.polygon.io/v2/last/trade/I:NDX?apiKey={API_KEY}"
try:
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {str(e)}")

# Test 2: Get NQ Futures (if available)
print("\n2. Testing NQ Futures")
url = f"https://api.polygon.io/v2/last/trade/NQ?apiKey={API_KEY}"
try:
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {str(e)}")

# Test 3: Get QQQ ETF (tracks NASDAQ-100)
print("\n3. Testing QQQ ETF (NASDAQ-100 tracker)")
url = f"https://api.polygon.io/v2/last/trade/QQQ?apiKey={API_KEY}"
try:
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {str(e)}")

# Test 4: Get Snapshot (recommended for real-time)
print("\n4. Testing Snapshot API (recommended)")
url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/QQQ?apiKey={API_KEY}"
try:
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {str(e)}")

# Test 5: Check API limits
print("\n5. Checking API Rate Limits")
print("   Free tier: 5 API calls per minute")
print("   Recommended: 12-second intervals (5 calls/min)")

print("\n" + "=" * 60)
print("📊 RECOMMENDATION:")
print("   Use QQQ (NASDAQ-100 ETF) as proxy for NQ futures")
print("   Endpoint: /v2/last/trade/QQQ")
print("   Or: /v2/snapshot/locale/us/markets/stocks/tickers/QQQ")
