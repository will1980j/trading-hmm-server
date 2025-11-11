import requests
import json

print("=== AUTOMATED SIGNALS WEBHOOK DIAGNOSIS ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

# 1. Check what webhook endpoints exist
print("1. CHECKING WEBHOOK ENDPOINTS:")
print("-" * 60)

endpoints_to_check = [
    '/api/automated-signals/webhook',
    '/api/automated-signals/signal',
    '/api/automated-signals/create',
    '/api/live-signals',
]

for endpoint in endpoints_to_check:
    try:
        # Try GET first
        response = requests.get(f"{base_url}{endpoint}", timeout=5)
        print(f"{endpoint} (GET): {response.status_code}")
    except Exception as e:
        print(f"{endpoint} (GET): ERROR - {str(e)[:50]}")
    
    try:
        # Try POST with test payload
        test_payload = {
            "type": "signal_created",
            "signal_id": "TEST_123",
            "bias": "Bullish",
            "entry_price": 21000.50
        }
        response = requests.post(f"{base_url}{endpoint}", json=test_payload, timeout=5)
        print(f"{endpoint} (POST): {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"{endpoint} (POST): ERROR - {str(e)[:50]}")

print("\n2. CHECKING AUTOMATED SIGNALS API:")
print("-" * 60)

# Check stats endpoint
try:
    response = requests.get(f"{base_url}/api/automated-signals/stats", timeout=10)
    print(f"Stats endpoint: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Stats endpoint ERROR: {e}")

print("\n3. CHECKING DATABASE TABLE:")
print("-" * 60)

# Check if we can query the database
try:
    response = requests.get(f"{base_url}/api/automated-signals/recent", timeout=10)
    print(f"Recent signals endpoint: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Recent signals ERROR: {e}")

print("\n4. INDICATOR PAYLOAD FORMAT:")
print("-" * 60)
print("""
Your indicator sends this format:
{
  "type": "signal_created",
  "signal_id": "20241111_103045_BULLISH",
  "date": "2024-11-11",
  "time": "10:30:45",
  "bias": "Bullish",
  "session": "NY AM",
  "entry_price": 21000.50,
  "sl_price": 20975.25,
  "risk_distance": 25.25,
  "be_price": 21000.50,
  "target_1r": 21025.75,
  "target_2r": 21051.00,
  "target_3r": 21076.25,
  "be_hit": false,
  "be_mfe": 0.00,
  "no_be_mfe": 0.00,
  "status": "active",
  "timestamp": 1731340245000
}
""")

print("\n5. REQUIRED WEBHOOK ENDPOINT:")
print("-" * 60)
print("""
The webhook endpoint MUST:
1. Accept POST requests
2. Parse the JSON payload from the indicator
3. Save to automated_signals table
4. Broadcast via WebSocket to dashboard
5. Return success response to TradingView

Endpoint should be: /api/automated-signals/webhook
""")
