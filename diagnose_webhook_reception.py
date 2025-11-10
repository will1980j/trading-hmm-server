import requests
import json
from datetime import datetime

print("=" * 80)
print("WEBHOOK RECEPTION DIAGNOSTIC")
print("=" * 80)

base_url = "https://web-production-cd33.up.railway.app"

# 1. Check recent webhook stats
print("\n1. CHECKING WEBHOOK STATS...")
try:
    response = requests.get(f"{base_url}/api/webhook-stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Webhook Stats Retrieved:")
        print(f"   Total Webhooks: {stats.get('total_webhooks', 0)}")
        print(f"   Last Webhook: {stats.get('last_webhook_time', 'Never')}")
        print(f"   Recent Count: {stats.get('recent_count', 0)}")
    else:
        print(f"❌ Failed to get webhook stats: {response.status_code}")
except Exception as e:
    print(f"❌ Error getting webhook stats: {e}")

# 2. Check automated signals data
print("\n2. CHECKING AUTOMATED SIGNALS DATA...")
try:
    response = requests.get(f"{base_url}/api/automated-signals-data")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Automated Signals Data Retrieved:")
        print(f"   Total Signals: {data.get('total', 0)}")
        print(f"   Pending: {data.get('pending', 0)}")
        print(f"   Confirmed: {data.get('confirmed', 0)}")
        
        if data.get('signals'):
            print(f"\n   Recent Signals:")
            for sig in data['signals'][:3]:
                print(f"   - {sig.get('signal_id')}: {sig.get('status')} ({sig.get('bias')})")
        else:
            print("   ⚠️ No signals in database!")
    else:
        print(f"❌ Failed to get automated signals data: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error getting automated signals data: {e}")

# 3. Test webhook endpoint directly
print("\n3. TESTING WEBHOOK ENDPOINT...")
test_payload = {
    "type": "signal_created",
    "signal_id": "TEST_20241111_120000_BULLISH",
    "date": "2024-11-11",
    "time": "12:00:00",
    "bias": "Bullish",
    "session": "NY AM",
    "entry_price": 20500.00,
    "sl_price": 20497.50,
    "risk_distance": 2.50,
    "be_price": 20500.00,
    "target_1r": 20502.50,
    "target_2r": 20505.00,
    "target_3r": 20507.50,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": int(datetime.now().timestamp() * 1000)
}

try:
    response = requests.post(
        f"{base_url}/api/automated-signals",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print("✅ Test webhook accepted!")
    else:
        print(f"❌ Test webhook failed!")
except Exception as e:
    print(f"❌ Error testing webhook: {e}")

# 4. Check database connection
print("\n4. CHECKING DATABASE CONNECTION...")
try:
    response = requests.get(f"{base_url}/api/webhook-health")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ Database Health:")
        print(f"   Status: {health.get('database', 'unknown')}")
        print(f"   Connection: {health.get('connection', 'unknown')}")
    else:
        print(f"❌ Failed to get health status: {response.status_code}")
except Exception as e:
    print(f"❌ Error checking health: {e}")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
