import requests
import json

url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"

print("Testing dashboard-data endpoint...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    
    try:
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
        
        # Check for specific error message
        if not data.get('success'):
            print(f"\n❌ FAILED: {data.get('error', 'Unknown error')}")
            print(f"Message: {data.get('message', 'No message')}")
        else:
            print(f"\n✅ SUCCESS!")
            print(f"Active trades: {len(data.get('active_trades', []))}")
            print(f"Completed trades: {len(data.get('completed_trades', []))}")
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text[:500]}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
