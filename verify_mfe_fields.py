import requests

# Check what fields are in MFE_UPDATE events
url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    active = data.get('active_trades', [])
    
    if active:
        print("Sample active trade fields:")
        print(active[0].keys())
        print("\nSample trade:")
        for key, value in active[0].items():
            print(f"  {key}: {value}")
else:
    print(f"Error: {response.status_code}")
