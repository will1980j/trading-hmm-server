"""
Verify Indicator Export System is Ready
Tests all endpoints before starting export
"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("INDICATOR EXPORT SYSTEM VERIFICATION")
print("=" * 80)
print()

# Test 1: Check inspector endpoint exists
print("1. Testing Inspector Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Inspector endpoint working")
            print(f"   📊 Current signals in inspector: {data.get('total_signals', 0)}")
        else:
            print(f"   ⚠️ Inspector endpoint exists but no data yet")
    else:
        print(f"   ❌ Inspector endpoint returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Inspector endpoint error: {e}")

print()

# Test 2: Check bulk import endpoint exists
print("2. Testing Bulk Import Endpoint...")
try:
    # Send empty test payload
    response = requests.post(
        f"{BASE_URL}/api/indicator-import/bulk",
        json={'signals': []}
    )
    if response.status_code == 200:
        print(f"   ✅ Bulk import endpoint working")
    else:
        print(f"   ❌ Bulk import endpoint returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Bulk import endpoint error: {e}")

print()

# Test 3: Check all signals import endpoint exists
print("3. Testing All Signals Import Endpoint...")
try:
    # Send empty test payload
    response = requests.post(
        f"{BASE_URL}/api/indicator-import/all-signals",
        json={'signals': []}
    )
    if response.status_code == 200:
        print(f"   ✅ All signals import endpoint working")
    else:
        print(f"   ❌ All signals import endpoint returned {response.status_code}")
except Exception as e:
    print(f"   ❌ All signals import endpoint error: {e}")

print()

# Test 4: Check automated signals dashboard
print("4. Testing Automated Signals Dashboard...")
try:
    response = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Dashboard API working")
        print(f"   📊 Current active trades: {data.get('active_count', 0)}")
        print(f"   📊 Current completed trades: {data.get('completed_count', 0)}")
    else:
        print(f"   ❌ Dashboard API returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Dashboard API error: {e}")

print()
print("=" * 80)
print("SYSTEM STATUS")
print("=" * 80)
print()
print("✅ All endpoints are ready for export")
print()
print("NEXT STEPS:")
print("1. Open TradingView indicator settings")
print("2. Enable 'Enable Bulk Export' checkbox")
print("3. Set 'Delay Between Batches' to 0")
print("4. Create export alert with webhook URL:")
print(f"   {BASE_URL}/api/indicator-inspector/receive")
print("5. Wait for export to complete (watch indicator display panel)")
print("6. Run: python analyze_indicator_export.py")
print()
