#!/usr/bin/env python3
"""Query Railway's database directly through its API"""
import requests

# Get the debug data which shows actual database contents
print("=== RAILWAY DEBUG ENDPOINT (shows actual DB) ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/debug', timeout=30)
    data = resp.json()
    print(f"Entry count: {data.get('entry_count')}")
    print(f"Exit count: {data.get('exit_count')}")
    print("\nLast 10 records:")
    for rec in data.get('last_10_records', []):
        print(f"  ID={rec.get('id')}, trade={rec.get('trade_id')}, type={rec.get('event_type')}, ts={rec.get('timestamp')}")
except Exception as e:
    print(f"Error: {e}")

# Get dashboard data
print("\n=== DASHBOARD DATA ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
    data = resp.json()
    print(f"Active trades: {len(data.get('active_trades', []))}")
    print(f"Completed trades: {len(data.get('completed_trades', []))}")
    
    if data.get('active_trades'):
        print("\nFirst 3 active trades:")
        for t in data['active_trades'][:3]:
            print(f"  {t.get('trade_id')}: MFE={t.get('mfe')}, signal_time={t.get('signal_time')}")
except Exception as e:
    print(f"Error: {e}")

# Check what the stats-live endpoint shows
print("\n=== STATS-LIVE ENDPOINT ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/stats-live', timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
