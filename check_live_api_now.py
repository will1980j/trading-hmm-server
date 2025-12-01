#!/usr/bin/env python3
"""Check what the LIVE Railway API is returning RIGHT NOW"""
import requests
import json

BASE_URL = 'https://web-production-f8c3.up.railway.app'

print("=" * 70)
print("CHECKING LIVE RAILWAY API - NOT LOCAL CODE")
print("=" * 70)

# Get dashboard data
resp = requests.get(f'{BASE_URL}/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()

print(f"\nActive trades: {len(data.get('active_trades', []))}")
print(f"Completed trades: {len(data.get('completed_trades', []))}")

if data.get('active_trades'):
    print("\n=== FIRST 3 ACTIVE TRADES ===")
    for t in data['active_trades'][:3]:
        print(f"\ntrade_id: {t.get('trade_id')}")
        print(f"  signal_date: {t.get('signal_date')}")
        print(f"  signal_time: {t.get('signal_time')}")
        print(f"  timestamp: {t.get('timestamp')}")
        print(f"  session: {t.get('session')}")
        print(f"  be_mfe: {t.get('be_mfe')}")
        print(f"  no_be_mfe: {t.get('no_be_mfe')}")

if data.get('completed_trades'):
    print("\n=== FIRST 3 COMPLETED TRADES ===")
    for t in data['completed_trades'][:3]:
        print(f"\ntrade_id: {t.get('trade_id')}")
        print(f"  signal_date: {t.get('signal_date')}")
        print(f"  signal_time: {t.get('signal_time')}")
        print(f"  exit_timestamp: {t.get('exit_timestamp')}")
        print(f"  entry_timestamp: {t.get('entry_timestamp')}")
        print(f"  be_mfe: {t.get('be_mfe')}")
        print(f"  no_be_mfe: {t.get('no_be_mfe')}")
        print(f"  final_mfe: {t.get('final_mfe')}")

print("\n" + "=" * 70)
print("⚠️  These are from the LIVE Railway server")
print("⚠️  Local code changes have NOT been deployed yet")
print("⚠️  You need to commit and push via GitHub Desktop")
print("=" * 70)
