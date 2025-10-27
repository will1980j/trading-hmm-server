#!/usr/bin/env python3

import requests
import json

def test_v2_endpoints():
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print('Testing V2 endpoints...')
    print()
    
    # Test V2 stats (public endpoint)
    try:
        response = requests.get(f'{base_url}/api/v2/stats', timeout=10)
        print(f'V2 Stats: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Data keys: {list(data.keys())}')
            print(f'  Total signals: {data.get("total_signals", "N/A")}')
        else:
            print(f'  Error: {response.text[:200]}')
    except Exception as e:
        print(f'V2 Stats error: {e}')
    
    print()
    
    # Test V2 active trades (public endpoint)
    try:
        response = requests.get(f'{base_url}/api/v2/active-trades', timeout=10)
        print(f'V2 Active Trades: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Data keys: {list(data.keys())}')
            trades = data.get('trades', [])
            print(f'  Number of trades: {len(trades)}')
            if trades:
                print(f'  First trade keys: {list(trades[0].keys())}')
        else:
            print(f'  Error: {response.text[:200]}')
    except Exception as e:
        print(f'V2 Active Trades error: {e}')
    
    print()
    
    # Test V2 current price (public endpoint)
    try:
        response = requests.get(f'{base_url}/api/v2/price/current', timeout=10)
        print(f'V2 Current Price: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Data keys: {list(data.keys())}')
        else:
            print(f'  Error: {response.text[:200]}')
    except Exception as e:
        print(f'V2 Current Price error: {e}')

if __name__ == '__main__':
    test_v2_endpoints()