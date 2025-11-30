#!/usr/bin/env python3
"""Check what MFE data the API is returning"""
import requests

url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/hub-data'
try:
    resp = requests.get(url, timeout=30)
    data = resp.json()
    trades = data.get('trades', [])
    print(f'Total trades: {len(trades)}')
    if trades:
        print('\nFirst 5 trades MFE data:')
        for t in trades[:5]:
            print(f"  Trade {t.get('trade_id')}: be_mfe_R={t.get('be_mfe_R')}, no_be_mfe_R={t.get('no_be_mfe_R')}, status={t.get('status')}")
        
        # Check if any trades have MFE values
        with_be_mfe = [t for t in trades if t.get('be_mfe_R') is not None]
        with_no_be_mfe = [t for t in trades if t.get('no_be_mfe_R') is not None]
        print(f'\nTrades with be_mfe_R: {len(with_be_mfe)}/{len(trades)}')
        print(f'Trades with no_be_mfe_R: {len(with_no_be_mfe)}/{len(trades)}')
except Exception as e:
    print(f'Error: {e}')
