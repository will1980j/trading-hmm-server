"""
Analyze Indicator Export Data
Creates digestible report of the 2,125 signals
"""

import json
import requests
from collections import defaultdict
from datetime import datetime

print("=" * 80)
print("INDICATOR DATA ANALYSIS")
print("=" * 80)
print()

# Get summary from backend
url = "https://web-production-f8c3.up.railway.app/api/indicator-inspector/summary"
response = requests.get(url)

if response.status_code != 200:
    print("❌ No data received yet from indicator")
    print("   Run the indicator export first")
    exit(1)

data = response.json()

if not data.get('success'):
    print("❌ Error:", data.get('error'))
    exit(1)

print(f"Total Signals Received: {data['total_signals']}")
print(f"Active: {data['active']}")
print(f"Completed: {data['completed']}")
print()

print("Date Range:")
print(f"   Oldest: {data['date_range']['oldest']}")
print(f"   Newest: {data['date_range']['newest']}")
print()

print("Direction Breakdown:")
print(f"   Bullish: {data['direction']['bullish']}")
print(f"   Bearish: {data['direction']['bearish']}")
print()

print("=" * 80)
print("SAMPLE SIGNALS (First 5)")
print("=" * 80)

for i, signal in enumerate(data.get('sample_signals', []), 1):
    print(f"\n{i}. {signal.get('trade_id', 'N/A')}")
    print(f"   Date: {signal.get('date')}")
    print(f"   Direction: {signal.get('direction')}")
    print(f"   Entry: ${signal.get('entry')}")
    print(f"   Stop: ${signal.get('stop')}")
    print(f"   MFE: {signal.get('mfe')}R")
    print(f"   Status: {'COMPLETED' if signal.get('completed') else 'ACTIVE'}")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()
print("Based on this data, you can:")
print("1. Import all signals to database (if data looks good)")
print("2. Import only recent signals (last 30 days)")
print("3. Import only completed signals (for analysis)")
print("4. Discard and start fresh (if data quality is poor)")
