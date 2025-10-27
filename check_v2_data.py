#!/usr/bin/env python3

import requests

def check_v2_data():
    base_url = 'https://web-production-cd33.up.railway.app'
    
    # Check webhook stats
    try:
        response = requests.get(f'{base_url}/api/webhook-stats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print('Webhook Stats:')
            print(f'  Total webhooks: {data.get("total_webhooks", 0)}')
            print(f'  V2 webhooks: {data.get("v2_webhooks", 0)}')
            print(f'  Recent activity: {len(data.get("recent_activity", []))} items')
        else:
            print(f'Webhook stats error: {response.status_code}')
    except Exception as e:
        print(f'Webhook stats error: {e}')
    
    print()
    
    # Check if V2 webhook endpoint is working
    try:
        # Test with a sample signal
        test_signal = {
            "signal_type": "Bullish",
            "price": 4156.25,
            "session": "NY AM",
            "timestamp": "1698765432000"
        }
        
        response = requests.post(f'{base_url}/api/live-signals-v2', 
                               json=test_signal, timeout=10)
        print(f'V2 Webhook Test: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Response: {data}')
        else:
            print(f'  Error: {response.text[:200]}')
    except Exception as e:
        print(f'V2 Webhook test error: {e}')

if __name__ == '__main__':
    check_v2_data()