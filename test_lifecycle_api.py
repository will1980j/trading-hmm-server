"""Test the trade detail API"""
import requests

trade_id = "20251212_151200000_BEARISH"
url = f"https://web-production-f8c3.up.railway.app/api/automated-signals/trade-detail/{trade_id}"

print(f"Testing: {url}")
print()

response = requests.get(url)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Events: {len(data.get('events', []))}")
    
    if data.get('events'):
        print("\nFirst event:")
        print(data['events'][0])
else:
    print(f"Error: {response.text}")
