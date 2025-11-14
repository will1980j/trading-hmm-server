"""
Check if backend is receiving webhooks by testing the endpoint directly
"""

import requests
import json
from datetime import datetime

# Test webhook endpoint with a sample ENTRY payload
test_payload = {
    "type": "ENTRY",
    "signal_id": "TEST_20251114_120000_BULLISH",
    "date": "2025-11-14",
    "time": "12:00:00",
    "bias": "Bullish",
    "session": "NY AM",
    "entry_price": 20000.0,
    "sl_price": 19950.0,
    "risk_distance": 50.0,
    "be_price": 20000.0,
    "target_1r": 20050.0,
    "target_2r": 20100.0,
    "target_3r": 20150.0,
    "be_hit": False,
    "be_mfe": 0.0,
    "no_be_mfe": 0.0,
    "status": "active",
    "timestamp": int(datetime.now().timestamp() * 1000)
}

print("=" * 80)
print("TESTING WEBHOOK ENDPOINT")
print("=" * 80)
print()

url = "https://web-production-cd33.up.railway.app/api/automated-signals/webhook"
print(f"Sending test ENTRY webhook to: {url}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print()

try:
    response = requests.post(url, json=test_payload, timeout=10)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    print()
    
    if response.status_code == 200:
        print("✅ Backend received and processed webhook successfully!")
        print()
        print("Now checking if it was stored in database...")
        
        # Check dashboard data
        dash_response = requests.get('https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data')
        if dash_response.status_code == 200:
            data = dash_response.json()
            active = data.get('active_trades', [])
            if any(t.get('trade_id') == 'TEST_20251114_120000_BULLISH' for t in active):
                print("✅ Test signal found in database!")
            else:
                print("❌ Test signal NOT in database - backend processing issue")
                print(f"   Active trades: {len(active)}")
    else:
        print(f"❌ Backend returned error: {response.status_code}")
        print("   This means backend is rejecting the webhook")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - backend may be down or slow")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend - Railway may be down")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()
print("If test webhook succeeded but real webhooks don't work:")
print("- TradingView alert message format is wrong")
print("- TradingView alert is sending to wrong URL")
print("- Payload structure from indicator doesn't match backend expectations")
print()
print("If test webhook failed:")
print("- Backend endpoint has issues")
print("- Backend is rejecting the payload format")
print("- Railway deployment is broken")
