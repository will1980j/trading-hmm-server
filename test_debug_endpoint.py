import requests
import json

print("=== TESTING DEBUG ENDPOINT ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Waiting for deployment...")
print("Press Enter after pushing and waiting 2-3 minutes...")
input()

print("\nChecking what's in the database...")
debug_url = f'{base_url}/api/automated-signals/debug'

try:
    response = requests.get(debug_url, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal records in database: {data.get('total_in_db', 0)}")
        print(f"\nLast 10 records:")
        print(json.dumps(data.get('last_10_records', []), indent=2))
        
        # Analyze the data
        if data.get('last_10_records'):
            print("\n" + "="*60)
            print("ANALYSIS:")
            print("="*60)
            
            event_types = set()
            for record in data['last_10_records']:
                event_types.add(record.get('event_type'))
            
            print(f"\nUnique event_type values found: {event_types}")
            print("\nThis tells us what the stats query should be looking for!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
