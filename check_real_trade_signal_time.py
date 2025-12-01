#!/usr/bin/env python3
"""Check signal_time for REAL trade IDs (not test ones)"""
import requests

print("=== CHECKING REAL TRADE IDs FROM RAILWAY ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
    data = resp.json()
    
    # Filter to only real trade IDs (starting with date format)
    print("\nACTIVE TRADES (real trade IDs only):")
    for t in data.get('active_trades', []):
        trade_id = t.get('trade_id', '')
        # Skip test trades
        if trade_id.startswith('TEST') or trade_id.startswith('RAILWAY'):
            continue
        print(f"  {trade_id}")
        print(f"    signal_date: {t.get('signal_date')}")
        print(f"    signal_time: {t.get('signal_time')}")
        print()
    
    print("\nCOMPLETED TRADES (real trade IDs only, first 5):")
    count = 0
    for t in data.get('completed_trades', []):
        trade_id = t.get('trade_id', '')
        if trade_id.startswith('TEST') or trade_id.startswith('RAILWAY'):
            continue
        if count >= 5:
            break
        print(f"  {trade_id}")
        print(f"    signal_date: {t.get('signal_date')}")
        print(f"    signal_time: {t.get('signal_time')}")
        print()
        count += 1
        
except Exception as e:
    print(f"Error: {e}")
