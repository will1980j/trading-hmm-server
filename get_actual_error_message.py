import requests
import json

# Test the endpoint and show the actual error
url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"

response = requests.get(url)
data = response.json()

print("Response from dashboard-data endpoint:")
print(json.dumps(data, indent=2))

print("\n" + "="*60)
print("KEY FINDINGS:")
print("="*60)

if not data.get('success'):
    print(f"❌ Failed with error: {data.get('error')}")
    print(f"❌ Message: {data.get('message')}")
    
    # The message field should contain the actual exception
    if data.get('message') == '0':
        print("\n⚠️  PROBLEM: Message is '0' instead of actual error!")
        print("This means the exception is being caught but str(e) returns '0'")
        print("This is unusual - checking if there's a different error path...")
    
if 'debug_info' in data:
    print(f"\n📊 Debug Info:")
    for key, value in data['debug_info'].items():
        print(f"  {key}: {value}")
