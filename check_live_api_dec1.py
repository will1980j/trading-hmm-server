#!/usr/bin/env python3
"""Check what the live API is returning right now"""
import requests
import json

url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data'
try:
    resp = requests.get(url, timeout=30)
    data = resp.json()
    
    print('=== LIVE API RESPONSE ===')
    print(f'Active trades: {len(data.get("active_trades", []))}')
    print(f'Completed trades: {len(data.get("completed_trades", []))}')
    
    if data.get('active_trades'):
        print('\n=== FIRST 3 ACTIVE TRADES ===')
        for t in data['active_trades'][:3]:
            print(f"Trade: {t.get('trade_id')}")
            print(f"  Signal Time: {t.get('signal_time')}")
            print(f"  Signal Date: {t.get('signal_date')}")
            print(f"  MFE: {t.get('mfe')}")
            print(f"  BE MFE: {t.get('be_mfe')}")
            print(f"  Age: {t.get('age')}")
            print()
    
    if data.get('completed_trades'):
        print('\n=== FIRST 3 COMPLETED TRADES ===')
        for t in data['completed_trades'][:3]:
            print(f"Trade: {t.get('trade_id')}")
            print(f"  Signal Time: {t.get('signal_time')}")
            print(f"  Signal Date: {t.get('signal_date')}")
            print(f"  MFE: {t.get('mfe')}")
            print(f"  Age: {t.get('age')}")
            print()
            
except Exception as e:
    print(f'Error: {e}')
