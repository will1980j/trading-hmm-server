import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    print(f'Active: {len(data.get("active_trades", []))}')
    print(f'Completed: {len(data.get("completed_trades", []))}')
else:
    print(f'Error: {r.text[:500]}')
