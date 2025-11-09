"""
Simple webhook test to diagnose the issue
"""

import requests
import json

WEBHOOK_URL = "https://web-production-cd33.up.railway.app/api/automated-signals"

# Test with minimal data
payload = {
    "event_type": "ENTRY",
    "trade_id": "SIMPLE_TEST",
    "direction": "LONG",
    "entry_price": 21250.5,
    "stop_loss": 21225.5
}

print("Testing webhook with minimal payload...")
print(f"URL: {WEBHOOK_URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try to parse as JSON
    try:
        data = response.json()
        print(f"\nParsed JSON:")
        print(json.dumps(data, indent=2))
    except:
        print("\nCouldn't parse as JSON")
        
except Exception as e:
    print(f"\nError: {str(e)}")
