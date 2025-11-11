import requests
import json

print("=== TESTING DASHBOARD DATA ENDPOINT ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Testing /api/automated-signals/dashboard-data...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/dashboard-data', timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data.get('success')}")
        print(f"Active trades: {len(data.get('active_trades', []))}")
        print(f"Completed trades: {len(data.get('completed_trades', []))}")
        
        if data.get('active_trades'):
            print(f"\nFirst active trade:")
            print(json.dumps(data['active_trades'][0], indent=2))
        
        if len(data.get('active_trades', [])) == 0 and len(data.get('completed_trades', [])) == 0:
            print("\n✗ ENDPOINT RETURNS EMPTY DATA")
            print("Checking debug endpoint...")
            
            debug_response = requests.get(f'{base_url}/api/automated-signals/debug', timeout=10)
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print(f"Debug shows {debug_data.get('entry_count', 0)} ENTRY records in database")
                print("\nThe dashboard-data endpoint query is wrong!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Open browser console (F12) on the dashboard and check for:")
print("- JavaScript errors")
print("- Failed API calls")
print("- Empty signals array")
print("="*60)
