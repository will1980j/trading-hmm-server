import requests
import json

# Test batch webhook
batch_payload = {
    "event_type": "MFE_UPDATE_BATCH",
    "timestamp": "2025-12-09T22:30:00",
    "signals": [
        {
            "trade_id": "20251209_100400000_BULLISH",
            "direction": "Bullish",
            "be_mfe": 1.5,
            "no_be_mfe": 1.5,
            "mae_global_r": -0.2,
            "current_price": 25680.00,
            "be_triggered": False
        },
        {
            "trade_id": "20251209_103900000_BULLISH",
            "direction": "Bullish",
            "be_mfe": 2.3,
            "no_be_mfe": 2.8,
            "mae_global_r": -0.1,
            "current_price": 25685.50,
            "be_triggered": True
        }
    ]
}

print("Sending test batch webhook...")
r = requests.post(
    'https://web-production-f8c3.up.railway.app/api/automated-signals/webhook',
    json=batch_payload,
    headers={'Content-Type': 'application/json'}
)

print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

if r.status_code == 200:
    print("\n✅ Batch webhook processed successfully!")
    print("Check database for new MFE_UPDATE rows")
else:
    print(f"\n❌ Batch webhook failed: {r.text}")
