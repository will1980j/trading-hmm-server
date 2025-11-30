import requests
import json

# Check raw database data via debug endpoint
debug_url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/debug'
r = requests.get(debug_url, timeout=30)

print('=== DEBUG ENDPOINT RESPONSE ===')
print('Status:', r.status_code)

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2, default=str)[:3000])
else:
    print('Response:', r.text[:500])

# Check a specific recent trade
print('\n=== CHECKING RECENT ENTRY EVENTS ===')
dashboard_url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data'
dr = requests.get(dashboard_url, timeout=30)
data = dr.json()

# Look at the raw structure of active trades
active = data.get('active_trades', [])
if active:
    print('Sample active trade structure:')
    print(json.dumps(active[0], indent=2, default=str))
    
    # Check for our test trades
    test_trades = [t for t in active if 'TEST_' in str(t.get('trade_id', ''))]
    if test_trades:
        print('\nTest trade data:')
        print(json.dumps(test_trades[0], indent=2, default=str))
