"""
Check if webhook was received in the last few minutes
"""
import requests
from datetime import datetime, timedelta

# Check Railway logs via a test webhook
webhook_url = "https://web-production-cd33.up.railway.app/api/automated-signals"

print("🔍 Checking Recent Webhook Activity\n")
print("=" * 60)

# Send a test to see if endpoint is responding
test_payload = {
    "type": "signal_created",
    "signal_id": "TEST_CHECK_" + datetime.now().strftime("%H%M%S"),
    "date": datetime.now().strftime("%Y-%m-%d"),
    "time": datetime.now().strftime("%H:%M:%S"),
    "bias": "Bearish",
    "session": "NY PM",
    "entry_price": 20000.00,
    "sl_price": 20010.00,
    "risk_distance": 10.0,
    "be_price": 20000.00,
    "target_1r": 19990.00,
    "target_2r": 19980.00,
    "target_3r": 19970.00,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": int(datetime.now().timestamp() * 1000)
}

print("\n📤 Sending test webhook to verify endpoint is working...")
response = requests.post(webhook_url, json=test_payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    print("\n✅ Webhook endpoint is working!")
    print("\n🔍 Possible reasons your signal didn't appear:")
    print("1. TradingView alert didn't fire (check alert log)")
    print("2. Alert message is empty (should be empty for strategy)")
    print("3. Strategy hasn't confirmed the trade yet (waiting for confirmation candle)")
    print("4. Alert frequency is wrong (should be 'All')")
    print("\n📋 Check TradingView:")
    print("   - Click Alerts panel")
    print("   - Look for your alert")
    print("   - Check 'Times triggered' count")
    print("   - Click alert to see log")
else:
    print(f"\n❌ Webhook endpoint error: {response.status_code}")
    print("Railway might be down or restarting")

print("\n" + "=" * 60)
