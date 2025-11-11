import requests
import json
from datetime import datetime

print("=== TESTING WEBHOOK RECEPTION ===\n")

# Test if webhook endpoint is accessible
webhook_url = 'https://web-production-cd33.up.railway.app/api/live-signals-v2-complete'

# Simulate a TradingView signal
test_payload = {
    "signal_type": "Bullish",
    "signal_price": 21000.50,
    "signal_time": datetime.utcnow().isoformat(),
    "session": "NY AM",
    "htf_alignment": "1H:Bullish 15M:Bullish 5M:Bullish",
    "signal_source": "FVG",
    "raw_signal_data": "TEST:Bullish:21000.50:85.0:1H:Bullish 15M:Bullish 5M:Bullish:FVG:1731340800000"
}

print("Testing webhook endpoint...")
print(f"URL: {webhook_url}")
print(f"Payload: {json.dumps(test_payload, indent=2)}\n")

try:
    response = requests.post(webhook_url, json=test_payload, timeout=10)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}\n")
    
    if response.status_code == 200:
        print("✓ Webhook endpoint is working!")
        
        # Check if signal was saved
        print("\nChecking if signal was saved...")
        stats_url = 'https://web-production-cd33.up.railway.app/api/automated-signals/stats'
        stats_response = requests.get(stats_url, timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"Total signals now: {stats.get('stats', {}).get('total_signals', 0)}")
    else:
        print(f"✗ Webhook endpoint returned error: {response.status_code}")
        
except Exception as e:
    print(f"✗ Error testing webhook: {e}")

print("\n" + "="*60)
print("CHECKING TRADINGVIEW ALERT CONFIGURATION:")
print("="*60)

print("""
Your TradingView alert should be configured as:

Webhook URL: https://web-production-cd33.up.railway.app/api/live-signals-v2-complete

Alert Message Format (JSON):
{
  "signal_type": "{{strategy.order.action}}",
  "signal_price": {{close}},
  "signal_time": "{{time}}",
  "session": "NY AM",
  "htf_alignment": "1H:Bullish 15M:Bullish 5M:Bullish",
  "signal_source": "FVG",
  "raw_signal_data": "SIGNAL:{{strategy.order.action}}:{{close}}:85.0:1H:Bullish:FVG:{{time}}"
}

OR if using the indicator's built-in alert message, just send:
{{plot_0}}

Make sure:
1. Webhook URL is exactly correct
2. Alert is set to "Once Per Bar Close" 
3. Alert is ACTIVE (not paused)
4. You're testing on a live/replay chart (not historical)
""")

print("\n" + "="*60)
print("CHECKING ALTERNATIVE WEBHOOK ENDPOINTS:")
print("="*60)

# Check other webhook endpoints
endpoints = [
    '/api/live-signals',
    '/api/live-signals-v2',
    '/api/live-signals-v2-complete'
]

base_url = 'https://web-production-cd33.up.railway.app'
for endpoint in endpoints:
    try:
        response = requests.post(f"{base_url}{endpoint}", json=test_payload, timeout=5)
        print(f"{endpoint}: {response.status_code}")
    except Exception as e:
        print(f"{endpoint}: ERROR - {e}")
