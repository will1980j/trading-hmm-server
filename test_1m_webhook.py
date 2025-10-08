import requests
import json

# Test sending a 1m signal to your webhook
webhook_url = "https://web-production-cd33.up.railway.app/api/live-signals"

test_signal = {
    "symbol": "NQ1!",
    "timeframe": "1m",
    "bias": "Bullish",
    "price": 21094.50,
    "strength": 85,
    "htf_aligned": True,
    "htf_status": "ALIGNED",
    "signal_type": "BIAS_BULLISH"
}

print("Sending test 1m signal...")
response = requests.post(webhook_url, json=test_signal)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
