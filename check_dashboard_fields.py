#!/usr/bin/env python3
"""Check all fields returned by dashboard-data endpoint"""
import requests
import json

print("=== DASHBOARD-DATA FULL RESPONSE ===")
try:
    resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
    data = resp.json()
    
    # Show structure of first active trade
    if data.get('active_trades'):
        print("\n=== FIRST ACTIVE TRADE (all fields) ===")
        first = data['active_trades'][0]
        for key, value in sorted(first.items()):
            print(f"  {key}: {value}")
    
    # Show structure of first completed trade
    if data.get('completed_trades'):
        print("\n=== FIRST COMPLETED TRADE (all fields) ===")
        first = data['completed_trades'][0]
        for key, value in sorted(first.items()):
            print(f"  {key}: {value}")
    
    # Show stats
    if data.get('stats'):
        print("\n=== STATS ===")
        for key, value in sorted(data['stats'].items()):
            print(f"  {key}: {value}")
            
except Exception as e:
    print(f"Error: {e}")

# Also check what the trade_id format tells us about timing
print("\n=== PARSING TRADE_ID FOR TIME INFO ===")
trade_ids = [
    '20251201_001100000_BULLISH',  # Should be 00:11:00 on Dec 1
    '20251130_195200000_BEARISH',  # Should be 19:52:00 on Nov 30
]
for tid in trade_ids:
    parts = tid.split('_')
    if len(parts) >= 2:
        date_part = parts[0]  # YYYYMMDD
        time_part = parts[1]  # HHMMSS000
        
        year = date_part[:4]
        month = date_part[4:6]
        day = date_part[6:8]
        
        hour = time_part[:2]
        minute = time_part[2:4]
        second = time_part[4:6]
        
        print(f"  {tid}")
        print(f"    Date: {year}-{month}-{day}")
        print(f"    Time: {hour}:{minute}:{second}")
