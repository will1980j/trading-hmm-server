import requests
import json

# Test the production API
r = requests.get('https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print('API Response Keys:', list(data.keys()))
print('\nActive Trades Count:', len(data.get('active_trades', [])))
print('Completed Trades Count:', len(data.get('completed_trades', [])))

if data.get('active_trades'):
    print('\nFirst Active Trade Keys:', list(data['active_trades'][0].keys()))
    print('\nFirst Active Trade has date field:', 'date' in data['active_trades'][0])
    print('Date value:', data['active_trades'][0].get('date', 'MISSING'))
    print('\nFull first trade:')
    print(json.dumps(data['active_trades'][0], indent=2, default=str))
else:
    print('\nNo active trades to check')

if data.get('completed_trades'):
    print('\nFirst Completed Trade has date field:', 'date' in data['completed_trades'][0])
    print('Date value:', data['completed_trades'][0].get('date', 'MISSING'))
