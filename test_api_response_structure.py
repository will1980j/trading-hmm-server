"""Test the actual API response structure"""
import requests
import json

trade_id = "20251212_151200000_BEARISH"
url = f"https://web-production-f8c3.up.railway.app/api/automated-signals/trade-detail/{trade_id}"

print(f"Testing: {url}")
print()

response = requests.get(url)
print(f"Status: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    print("Response structure:")
    print(json.dumps(data, indent=2, default=str)[:2000])
    
    if data.get('success'):
        detail = data.get('data', {})
        print()
        print("=" * 80)
        print("DETAIL OBJECT:")
        print(f"   trade_id: {detail.get('trade_id')}")
        print(f"   direction: {detail.get('direction')}")
        print(f"   status: {detail.get('status')}")
        print(f"   entry_price: {detail.get('entry_price')}")
        print(f"   stop_loss: {detail.get('stop_loss')}")
        print(f"   risk_distance: {detail.get('risk_distance')}")
        print(f"   be_mfe: {detail.get('be_mfe')}")
        print(f"   no_be_mfe: {detail.get('no_be_mfe')}")
        print(f"   mae_global_R: {detail.get('mae_global_R')}")
        print(f"   events: {len(detail.get('events', []))} events")
        
        if detail.get('events'):
            print()
            print("First event:")
            print(json.dumps(detail['events'][0], indent=2, default=str))
else:
    print(f"Error: {response.text}")
