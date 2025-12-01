#!/usr/bin/env python3
"""Diagnose trade times - compare what's in the system vs TradingView"""
import requests
from datetime import datetime

# Get all trades from the API
resp = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data', timeout=30)
data = resp.json()

print("=" * 80)
print("TRADE TIME ANALYSIS - Nov 30, 2025 Trades")
print("=" * 80)

# Combine active and completed
all_trades = data.get('active_trades', []) + data.get('completed_trades', [])

# Filter for Nov 30 trades
nov30_trades = []
for t in all_trades:
    trade_id = t.get('trade_id', '')
    if trade_id.startswith('20251130'):
        nov30_trades.append(t)

# Sort by trade_id
nov30_trades.sort(key=lambda x: x.get('trade_id', ''))

print(f"\nFound {len(nov30_trades)} trades from Nov 30, 2025\n")

print(f"{'Trade ID':<40} {'Direction':<10} {'Signal Time':<15} {'Parsed Time':<15} {'Status'}")
print("-" * 100)

for t in nov30_trades:
    trade_id = t.get('trade_id', '')
    direction = t.get('direction', '')
    signal_time = t.get('signal_time', 'N/A')
    event_type = t.get('event_type', 'ACTIVE')
    
    # Parse time from trade_id: YYYYMMDD_HHMMSS000_DIRECTION
    # Format: 20251130_180800000_BEARISH
    try:
        parts = trade_id.split('_')
        if len(parts) >= 2:
            time_part = parts[1][:6]  # HHMMSS
            hh = time_part[0:2]
            mm = time_part[2:4]
            ss = time_part[4:6]
            parsed_time = f"{hh}:{mm}:{ss}"
        else:
            parsed_time = "PARSE_ERR"
    except:
        parsed_time = "PARSE_ERR"
    
    status = "COMPLETED" if "EXIT" in event_type else "ACTIVE"
    
    print(f"{trade_id:<40} {direction:<10} {signal_time:<15} {parsed_time:<15} {status}")

print("\n" + "=" * 80)
print("EXPECTED TIMES FROM TRADINGVIEW SCREENSHOT:")
print("=" * 80)
print("""
Based on your screenshot, the signals should be at:
- 18:08 - Completed (After Hours)
- 18:26 - Active (After Hours)  
- 18:39 - Active (After Hours)
- 18:45 - Completed (After Hours)
- 19:02 - Active (After Hours)
- 19:14 - Completed (After Hours)
- 19:19 - Active

These times appear to be in Eastern Time (US/Eastern).
""")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
print("""
The trade_id format is: YYYYMMDD_HHMMSS000_DIRECTION

The time in the trade_id SHOULD match the TradingView signal time.
If they don't match, the issue is in how the indicator generates the trade_id.

Key questions:
1. What timezone is TradingView using when generating the trade_id?
2. Is the indicator using the correct timestamp function?
3. Is there a timezone conversion happening somewhere?
""")
