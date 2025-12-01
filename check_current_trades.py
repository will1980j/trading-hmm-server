#!/usr/bin/env python3
"""Check if current trades are real or stale"""
import requests
from datetime import datetime

resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()

print('=== ACTIVE TRADES ===')
for t in data.get('active_trades', [])[:10]:
    trade_id = t.get('trade_id', '')
    # Parse date from trade_id format: YYYYMMDD_HHMMSS000_DIRECTION
    if trade_id and '_' in trade_id:
        parts = trade_id.split('_')
        if len(parts) >= 2 and len(parts[0]) == 8:
            date_str = parts[0]
            print(f"  {trade_id} - Date: {date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} - {t.get('direction')}")
        else:
            print(f"  {trade_id} - {t.get('direction')} (non-standard format)")
    else:
        print(f"  {trade_id} - {t.get('direction')}")

print(f'\nTotal active: {len(data.get("active_trades", []))}')

print('\n=== COMPLETED TRADES (last 10) ===')
for t in data.get('completed_trades', [])[:10]:
    trade_id = t.get('trade_id', '')
    if trade_id and '_' in trade_id:
        parts = trade_id.split('_')
        if len(parts) >= 2 and len(parts[0]) == 8:
            date_str = parts[0]
            print(f"  {trade_id} - Date: {date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} - {t.get('event_type')}")
        else:
            print(f"  {trade_id} - {t.get('event_type')} (non-standard format)")
    else:
        print(f"  {trade_id} - {t.get('event_type')}")

print(f'\nTotal completed: {len(data.get("completed_trades", []))}')

# Check for today's date
today = datetime.now().strftime('%Y%m%d')
print(f"\n=== TODAY'S DATE: {today} ===")

today_active = [t for t in data.get('active_trades', []) if t.get('trade_id', '').startswith(today)]
today_completed = [t for t in data.get('completed_trades', []) if t.get('trade_id', '').startswith(today)]

print(f"Active trades from today: {len(today_active)}")
print(f"Completed trades from today: {len(today_completed)}")

# Check for Nov 30 trades
nov30 = '20251130'
nov30_active = [t for t in data.get('active_trades', []) if t.get('trade_id', '').startswith(nov30)]
nov30_completed = [t for t in data.get('completed_trades', []) if t.get('trade_id', '').startswith(nov30)]

print(f"\nNov 30 active trades: {len(nov30_active)}")
print(f"Nov 30 completed trades: {len(nov30_completed)}")
