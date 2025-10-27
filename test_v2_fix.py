#!/usr/bin/env python3

import requests
import time

def test_v2_fix():
    # Send another test signal to V2 webhook
    test_signal = {
        'signal_type': 'Bearish',
        'price': 4150.75,
        'session': 'NY PM',
        'timestamp': str(int(time.time() * 1000))
    }

    print('Sending test signal to V2 webhook...')
    response = requests.post('https://web-production-cd33.up.railway.app/api/live-signals-v2', 
                            json=test_signal, timeout=10)
    print(f'Webhook response: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        trade_id = data.get('v2_automation', {}).get('trade_id', 'N/A')
        print(f'Trade ID created: {trade_id}')

    print()
    print('Checking V2 active trades...')
    response = requests.get('https://web-production-cd33.up.railway.app/api/v2/active-trades', timeout=10)
    print(f'Active trades response: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        trades = data.get('trades', [])
        print(f'Number of trades found: {len(trades)}')
        for i, trade in enumerate(trades):
            trade_id = trade.get('id', 'N/A')
            bias = trade.get('bias', 'N/A')
            session = trade.get('session', 'N/A')
            print(f'  Trade {i+1}: ID={trade_id}, Bias={bias}, Session={session}')
    else:
        print(f'Error: {response.text[:200]}')

if __name__ == '__main__':
    test_v2_fix()