import requests
import json

# Check the dashboard-data endpoint
url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data'
r = requests.get(url, timeout=30)
data = r.json()

print('=== DASHBOARD DATA ANALYSIS ===')
print('Active trades:', len(data.get('active_trades', [])))
print('Completed trades:', len(data.get('completed_trades', [])))

# Show first few active trades
active = data.get('active_trades', [])
if active:
    print('\nFirst 5 active trades:')
    for t in active[:5]:
        print('  ', t.get('trade_id'), ':', t.get('direction'), '@', t.get('entry_price'))
else:
    print('\nNo active trades found!')

# Check stats
stats_url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/stats-live'
sr = requests.get(stats_url, timeout=30)
stats = sr.json()
print('\nStats response:', json.dumps(stats, indent=2))

# Check what the dashboard HTML route returns
print('\n=== CHECKING DASHBOARD ROUTE ===')
dashboard_url = 'https://web-production-f8c3.up.railway.app/automated-signals-dashboard'
dr = requests.get(dashboard_url, timeout=30, allow_redirects=True)
print('Dashboard URL status:', dr.status_code)
print('Final URL:', dr.url)
if dr.status_code == 200:
    # Check if it contains the expected elements
    html = dr.text
    if 'active-trades' in html or 'activeTrades' in html:
        print('Dashboard HTML contains active trades section')
    else:
        print('WARNING: Dashboard HTML may be missing active trades section')
    
    if 'loadDashboardData' in html or 'fetchDashboardData' in html:
        print('Dashboard has data loading function')
    else:
        print('WARNING: Dashboard may not have data loading function')
