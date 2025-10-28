"""
Diagnose Why Price Webhook Isn't Working
"""
import requests
from datetime import datetime
import pytz

BASE_URL = "https://web-production-cd33.up.railway.app"

print("🔍 DIAGNOSING PRICE WEBHOOK ISSUE")
print("=" * 60)

# Check current time and session
eastern = pytz.timezone('US/Eastern')
now = datetime.now(eastern)
hour = now.hour
minute = now.minute

print(f"\n⏰ CURRENT TIME: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Hour: {hour}, Minute: {minute}")

# Determine session
if (hour == 8 and minute >= 30) or (9 <= hour <= 11):
    session = "NY AM (PRIORITY)"
    should_stream = True
elif 13 <= hour <= 15:
    session = "NY PM (PRIORITY)"
    should_stream = True
elif hour == 12:
    session = "NY LUNCH"
    should_stream = True
elif 0 <= hour <= 5:
    session = "LONDON"
    should_stream = True
elif hour >= 6 and (hour < 8 or (hour == 8 and minute <= 29)):
    session = "NY PRE"
    should_stream = True
elif 20 <= hour <= 23:
    session = "ASIA"
    should_stream = True
else:
    session = "INVALID (16:00-19:59)"
    should_stream = False

print(f"   Session: {session}")
print(f"   Should Stream: {'YES' if should_stream else 'NO'}")

# Test webhook endpoint
print(f"\n📡 TESTING WEBHOOK ENDPOINT:")
print(f"   POST {BASE_URL}/api/realtime-price")

test_payload = {
    "type": "realtime_price",
    "symbol": "NQ",
    "price": 20000.00,
    "timestamp": int(datetime.now().timestamp() * 1000),
    "session": session.split()[0],
    "volume": 1000,
    "bid": 19999.75,
    "ask": 20000.25,
    "change": -5.50
}

try:
    response = requests.post(
        f"{BASE_URL}/api/realtime-price",
        json=test_payload,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 200:
        print("   ✅ Webhook endpoint is working!")
    else:
        print("   ❌ Webhook endpoint returned error")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Check if data was stored
print(f"\n📊 CHECKING IF DATA WAS STORED:")
try:
    response = requests.get(f"{BASE_URL}/api/v2/price/current", timeout=10)
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if data.get('status') == 'success':
        print(f"   ✅ Price data found: ${data.get('price')}")
        print(f"   Session: {data.get('session')}")
        print(f"   Timestamp: {data.get('timestamp')}")
    elif data.get('status') == 'no_data':
        print(f"   ⚠️  No price data in system")
        print(f"   Message: {data.get('message')}")
    else:
        print(f"   ❌ Unexpected response: {data}")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("🔍 DIAGNOSIS:")
print("=" * 60)

if should_stream:
    print("\n✅ Market is OPEN - price streamer SHOULD be sending data")
    print("\n❌ POSSIBLE ISSUES:")
    print("   1. TradingView indicator not running")
    print("      → Check if indicator is added to chart")
    print("      → Check if 'Enable Real-Time Price Streaming' is ON")
    print()
    print("   2. TradingView alert not configured")
    print("      → Alert must be set to 'Once Per Bar Close'")
    print("      → Webhook URL must be correct")
    print()
    print("   3. TradingView alert paused/disabled")
    print("      → Check alert list in TradingView")
    print("      → Ensure alert is active (not paused)")
    print()
    print("   4. Session filter blocking signals")
    print("      → Check 'Priority Sessions Only' setting")
    print("      → Current session must be valid")
    print()
    print("   5. Price change threshold not met")
    print("      → Default: 3.0 points minimum change")
    print("      → Check 'Minimum Price Change' setting")
else:
    print("\n⚠️  Market is CLOSED - price streamer should NOT send data")
    print("   This is expected behavior during INVALID session (16:00-19:59 EST)")

print("\n" + "=" * 60)
print("🔧 NEXT STEPS:")
print("=" * 60)
print("\n1. Check TradingView:")
print("   → Open your NASDAQ chart")
print("   → Verify 'NASDAQ Simple Price Streamer' indicator is active")
print("   → Check indicator settings (streaming enabled, session filters)")
print("   → Verify alert is created and active")
print()
print("2. Test webhook manually:")
print("   → Run this script again to send test data")
print("   → Check if test data appears on dashboard")
print()
print("3. Check Railway logs:")
print("   → Go to Railway dashboard")
print("   → View deployment logs")
print("   → Look for webhook POST requests")
print()
print("4. Verify webhook URL in TradingView:")
print(f"   → Should be: {BASE_URL}/api/realtime-price")
print("   → Check for typos or wrong URL")
