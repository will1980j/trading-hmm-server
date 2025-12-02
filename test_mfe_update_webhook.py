"""
Test MFE_UPDATE webhook manually
"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Send MFE_UPDATE for the active trade
payload = {
    "trade_id": "20251202_135100000_BULLISH",
    "event_type": "MFE_UPDATE",
    "mfe_R": 1.25,
    "current_price": 25625.0
}

print("Sending MFE_UPDATE webhook...")
print(f"Payload: {json.dumps(payload, indent=2)}")

r = requests.post(
    f"{BASE_URL}/api/automated-signals/webhook",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"\nResponse status: {r.status_code}")
print(f"Response: {r.text}")

# Check if it was stored
print("\n" + "=" * 80)
print("Checking dashboard data...")
r2 = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = r2.json()

if data.get('active_trades'):
    trade = data['active_trades'][0]
    print(f"BE MFE: {trade['be_mfe']}")
    print(f"No BE MFE: {trade['no_be_mfe']}")
    
    if trade['be_mfe'] > 0 or trade['no_be_mfe'] > 0:
        print("\n✅ MFE UPDATE WORKED!")
    else:
        print("\n❌ MFE STILL 0.00 - webhook failed or not stored")
