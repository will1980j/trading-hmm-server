#!/usr/bin/env python3
import requests
import json

BASE_URL = 'https://web-production-f8c3.up.railway.app'
resp = requests.get(f'{BASE_URL}/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()

print('=== ACTIVE TRADE SAMPLE ===')
if data.get('active_trades'):
    t = data['active_trades'][0]
    print(f"trade_id: {t.get('trade_id')}")
    print(f"timestamp: {t.get('timestamp')}")
    print(f"signal_date: {t.get('signal_date')}")
    print(f"signal_time: {t.get('signal_time')}")
    print(f"entry_timestamp: {t.get('entry_timestamp')}")
    print(f"session: {t.get('session')}")
    print(f"mfe: {t.get('mfe')}")
    print(f"be_mfe: {t.get('be_mfe')}")
    print(f"no_be_mfe: {t.get('no_be_mfe')}")
    print(f"All keys: {list(t.keys())}")
else:
    print("No active trades")

print()
print('=== COMPLETED TRADE SAMPLE ===')
if data.get('completed_trades'):
    t = data['completed_trades'][0]
    print(f"trade_id: {t.get('trade_id')}")
    print(f"timestamp: {t.get('timestamp')}")
    print(f"signal_date: {t.get('signal_date')}")
    print(f"signal_time: {t.get('signal_time')}")
    print(f"exit_timestamp: {t.get('exit_timestamp')}")
    print(f"session: {t.get('session')}")
    print(f"mfe: {t.get('mfe')}")
    print(f"be_mfe: {t.get('be_mfe')}")
    print(f"no_be_mfe: {t.get('no_be_mfe')}")
    print(f"final_mfe: {t.get('final_mfe')}")
else:
    print("No completed trades")

print()
print('=== CHECK MFE_UPDATE EVENTS IN DB ===')
# Check if there are MFE_UPDATE events
resp2 = requests.get(f'{BASE_URL}/api/automated-signals/trade-detail/20251130_172700000_BEARISH', timeout=30)
if resp2.status_code == 200:
    detail = resp2.json()
    print(f"Events for active trade: {len(detail.get('events', []))}")
    for e in detail.get('events', [])[:5]:
        print(f"  - {e.get('event_type')}: mfe={e.get('mfe')}, be_mfe={e.get('be_mfe')}, no_be_mfe={e.get('no_be_mfe')}")
else:
    print(f"Trade detail error: {resp2.status_code}")
