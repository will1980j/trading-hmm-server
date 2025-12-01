#!/usr/bin/env python3
"""Verify what signal_time is actually being returned"""
import requests
import json

print("=== RAW DASHBOARD-DATA RESPONSE ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
    data = resp.json()
    
    # Check first active trade for signal_time
    if data.get('active_trades'):
        print("\nFirst 3 active trades - signal_time field:")
        for t in data['active_trades'][:3]:
            print(f"  {t.get('trade_id')}")
            print(f"    signal_date: {t.get('signal_date')}")
            print(f"    signal_time: {t.get('signal_time')}")
            print(f"    timestamp: {t.get('timestamp')}")
            print()
    
    # Check first completed trade
    if data.get('completed_trades'):
        print("\nFirst 3 completed trades - signal_time field:")
        for t in data['completed_trades'][:3]:
            print(f"  {t.get('trade_id')}")
            print(f"    signal_date: {t.get('signal_date')}")
            print(f"    signal_time: {t.get('signal_time')}")
            print(f"    entry_timestamp: {t.get('entry_timestamp')}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
