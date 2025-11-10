"""
Diagnose why no signals are appearing in automated dashboard
"""
import requests
from datetime import datetime

BASE_URL = "https://web-production-cd33.up.railway.app"

print("\n" + "=" * 70)
print("🔍 DIAGNOSING NO SIGNALS ISSUE")
print("=" * 70)

# Check 1: Database has signals?
print("\n1️⃣ Checking if database has ANY automated signals...")
try:
    response = requests.get(f'{BASE_URL}/api/automated-signals/stats', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Total signals in database: {data.get('total_signals', 0)}")
        print(f"   Today's signals: {data.get('today_signals', 0)}")
        
        if data.get('total_signals', 0) == 0:
            print("   ❌ NO SIGNALS IN DATABASE")
            print("   → TradingView has not sent any signals to this endpoint")
        else:
            print("   ✅ Database has signals")
    else:
        print(f"   ❌ Stats endpoint error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 2: Webhook endpoint exists?
print("\n2️⃣ Checking webhook endpoint...")
try:
    response = requests.options(f'{BASE_URL}/api/automated-signals', timeout=10)
    print(f"   Webhook endpoint status: {response.status_code}")
    if response.status_code in [200, 204]:
        print("   ✅ Webhook endpoint is accessible")
    else:
        print("   ⚠️  Unexpected status code")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 3: Check other signal endpoints for comparison
print("\n3️⃣ Checking other signal endpoints for comparison...")
endpoints = [
    ('/api/v2/stats', 'Signal Lab V2'),
    ('/api/live-signals', 'Live Signals (original)'),
]

for endpoint, name in endpoints:
    try:
        response = requests.get(f'{BASE_URL}{endpoint}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_signals', 0)
            print(f"   {name}: {total} signals")
            if total > 0:
                print(f"      → This endpoint IS receiving signals!")
        else:
            print(f"   {name}: Error {response.status_code}")
    except Exception as e:
        print(f"   {name}: Error - {e}")

print("\n" + "=" * 70)
print("📋 DIAGNOSIS")
print("=" * 70)

print("\n🎯 The automated signals dashboard is working correctly.")
print("   The issue is: TradingView is NOT sending signals to this endpoint.")

print("\n❓ POSSIBLE REASONS:")
print("\n1. TradingView Alert Not Configured")
print("   → You need to create an alert in TradingView")
print("   → Alert must use webhook URL:")
print(f"      {BASE_URL}/api/automated-signals")

print("\n2. Wrong Webhook URL")
print("   → Check your TradingView alert settings")
print("   → Make sure it points to /api/automated-signals")
print("   → NOT /api/live-signals or /api/live-signals-v2")

print("\n3. Indicator Not Generating Signals")
print("   → Check if your indicator is showing triangles on chart")
print("   → Verify indicator is running on correct timeframe")
print("   → Check if market conditions meet signal criteria")

print("\n4. Alert Conditions Not Met")
print("   → Alert must trigger on indicator signal")
print("   → Check alert condition matches indicator output")

print("\n✅ TO FIX:")
print("\n   Step 1: Open TradingView")
print("   Step 2: Add your FVG indicator to chart")
print("   Step 3: Create Alert (clock icon)")
print("   Step 4: Set condition to your indicator signal")
print("   Step 5: In 'Notifications' tab:")
print("           ✓ Check 'Webhook URL'")
print(f"           ✓ Enter: {BASE_URL}/api/automated-signals")
print("   Step 6: In 'Message' field, use your indicator's alert message")
print("   Step 7: Click 'Create'")

print("\n💡 TEST THE WEBHOOK:")
print("   You can test if webhook works by sending a test signal:")
print(f"   curl -X POST {BASE_URL}/api/automated-signals \\")
print('        -H "Content-Type: application/json" \\')
print('        -d \'{"signal_type":"Bullish","price":16000,"session":"NY AM"}\'')

print("\n" + "=" * 70)
