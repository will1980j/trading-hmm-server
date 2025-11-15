"""
Debug the system health API response
"""
import requests
import json

url = 'https://web-production-cd33.up.railway.app/api/system-health'

print("🔍 Fetching system health data...\n")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}\n")
    
    data = response.json()
    
    print("=" * 60)
    print("FULL API RESPONSE:")
    print("=" * 60)
    print(json.dumps(data, indent=2))
    print("\n")
    
    print("=" * 60)
    print("COMPONENT BREAKDOWN:")
    print("=" * 60)
    
    if 'components' in data:
        for component_name, component_data in data['components'].items():
            print(f"\n{component_name.upper()}:")
            print(f"  Status: {component_data.get('status')}")
            print(f"  Data: {json.dumps(component_data, indent=4)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
