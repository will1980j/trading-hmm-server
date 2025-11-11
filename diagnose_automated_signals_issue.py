import requests
import json

base_url = 'https://web-production-cd33.up.railway.app'

print('=== Testing Automated Signals Endpoints ===\n')

# Test dashboard data endpoint
try:
    print('1. Testing /api/automated-signals/dashboard-data')
    response = requests.get(f'{base_url}/api/automated-signals/dashboard-data', timeout=10)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Response keys: {list(data.keys())}')
        print(f'   Signals count: {len(data.get("signals", []))}')
    else:
        print(f'   Error: {response.text[:200]}')
except Exception as e:
    print(f'   Exception: {e}')

print()

# Test stats endpoint
try:
    print('2. Testing /api/automated-signals/stats')
    response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Stats: {json.dumps(data, indent=2)}')
    else:
        print(f'   Error: {response.text[:200]}')
except Exception as e:
    print(f'   Exception: {e}')

print()

# Check if there's data in the database
try:
    print('3. Testing /api/webhook-stats (to see if webhooks are working)')
    response = requests.get(f'{base_url}/api/webhook-stats', timeout=10)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Total signals: {data.get("total_signals", 0)}')
        print(f'   Last 24h: {data.get("last_24h", 0)}')
    else:
        print(f'   Error: {response.text[:200]}')
except Exception as e:
    print(f'   Exception: {e}')

print()

# Check recent signals
try:
    print('4. Testing /api/live-signals (last 10)')
    response = requests.get(f'{base_url}/api/live-signals?limit=10', timeout=10)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        signals = data.get('signals', [])
        print(f'   Signals found: {len(signals)}')
        if signals:
            latest = signals[0]
            print(f'   Latest signal: {latest.get("signal_type")} at {latest.get("timestamp")}')
    else:
        print(f'   Error: {response.text[:200]}')
except Exception as e:
    print(f'   Exception: {e}')
