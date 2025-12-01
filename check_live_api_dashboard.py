#!/usr/bin/env python3
"""Check what the live Railway API is returning"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Check the dashboard data endpoint
print("Checking /api/automated-signals/dashboard-data...")
resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Active trades: {len(data.get('active_trades', []))}")
    print(f"Completed trades: {len(data.get('completed_trades', []))}")
    
    print("\n--- ACTIVE TRADES ---")
    for t in data.get('active_trades', []):
        print(f"  {t.get('trade_id')}: {t.get('direction')} @ {t.get('signal_time')} - MFE: {t.get('be_mfe')}")
    
    print("\n--- COMPLETED TRADES ---")
    for t in data.get('completed_trades', [])[:5]:
        print(f"  {t.get('trade_id')}: {t.get('direction')} @ {t.get('signal_time')} - MFE: {t.get('be_mfe')}")
else:
    print(resp.text[:500])

# Also check stats
print("\n\nChecking /api/automated-signals/stats-live...")
resp = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(resp.json())
