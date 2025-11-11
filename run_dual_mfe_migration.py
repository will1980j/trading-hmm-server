import requests
import json

url = "https://web-production-cd33.up.railway.app/api/add-dual-mfe-columns"

print("Running dual MFE column migration...")
print(f"URL: {url}\n")

try:
    response = requests.post(url, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse:")
    print(json.dumps(data, indent=2))
    
    if data.get('success'):
        print(f"\n✅ SUCCESS!")
        print(f"   {data.get('message')}")
        print(f"   Columns added: {', '.join(data.get('columns_added', []))}")
    else:
        print(f"\n❌ FAILED: {data.get('error')}")
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")
