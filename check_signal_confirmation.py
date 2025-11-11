import requests
import json
from datetime import datetime, timedelta

print("=== CHECKING SIGNAL CONFIRMATION ISSUE ===\n")

# Check webhook stats
url = 'https://web-production-cd33.up.railway.app/api/automated-signals/stats'
try:
    response = requests.get(url, timeout=10)
    print('WEBHOOK STATS:')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        stats = response.json()
        print(json.dumps(stats, indent=2))
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error checking stats: {e}')

print('\n' + '='*60)
print('RECENT SIGNALS (Last 10):')
print('='*60)

# Check recent signals
signals_url = 'https://web-production-cd33.up.railway.app/api/automated-signals/recent'
try:
    response = requests.get(signals_url, timeout=10)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        signals = response.json()
        if signals:
            for i, sig in enumerate(signals[:10], 1):
                print(f"\n{i}. ID: {sig.get('id')}")
                print(f"   Type: {sig.get('signal_type')}")
                print(f"   Time: {sig.get('signal_time')}")
                print(f"   Status: {sig.get('status')}")
                print(f"   Session: {sig.get('session')}")
                if sig.get('confirmation_time'):
                    print(f"   Confirmed: {sig.get('confirmation_time')}")
        else:
            print('No signals found in database')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error checking signals: {e}')

print('\n' + '='*60)
print('CHECKING LAST 5 MINUTES:')
print('='*60)

try:
    response = requests.get(signals_url, timeout=10)
    if response.status_code == 200:
        signals = response.json()
        if signals:
            latest = signals[0]
            print(f"\nLatest signal details:")
            print(json.dumps(latest, indent=2))
        else:
            print('No signals found')
except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*60)
print('DASHBOARD API CHECK:')
print('='*60)

# Check what the dashboard is actually fetching
dashboard_url = 'https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data'
try:
    response = requests.get(dashboard_url, timeout=10)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f"Active signals: {len(data.get('active_signals', []))}")
        print(f"Confirmed today: {len(data.get('confirmed_today', []))}")
        print(f"Pending signals: {len(data.get('pending_signals', []))}")
        
        if data.get('confirmed_today'):
            print("\nConfirmed signals today:")
            for sig in data['confirmed_today']:
                print(f"  - {sig.get('signal_type')} at {sig.get('confirmation_time')}")
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')
