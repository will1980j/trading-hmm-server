import requests
import json

# Test sending an MFE_UPDATE webhook
url = "https://web-production-cd33.up.railway.app/api/automated-signals/webhook"

# Use one of the existing trade IDs
payload = {
    "type": "MFE_UPDATE",
    "signal_id": "20251114_143700000_BEARISH",
    "current_price": 25100.00,
    "be_mfe": 1.5,
    "no_be_mfe": 1.5
}

print("Sending test MFE_UPDATE webhook...")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(url, json=payload)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\n✅ Webhook accepted! Now check dashboard...")
else:
    print("\n❌ Webhook failed!")
