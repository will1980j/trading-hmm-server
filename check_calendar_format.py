#!/usr/bin/env python3
"""Check signal_date format from API vs calendar selectedDate format"""
import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

trades = data.get('active_trades', []) + data.get('completed_trades', [])

print("Sample signal_date formats from API:")
print("-" * 50)
for t in trades[:10]:
    trade_id = t.get('trade_id', 'N/A')
    signal_date = t.get('signal_date', 'N/A')
    print(f"  trade_id: {trade_id}")
    print(f"  signal_date: {signal_date}")
    print()

print("\nCalendar selectedDate format: YYYY-MM-DD (e.g., 2025-12-02)")
print("\nIf signal_date is null or different format, filtering won't work!")
