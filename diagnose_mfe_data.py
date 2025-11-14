"""
Diagnose what MFE data is actually being returned by the API
"""

import requests
import json

# Test the dashboard data endpoint
url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"

print("Fetching dashboard data from API...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    print("\n" + "="*80)
    print("ACTIVE TRADES (first 3):")
    print("="*80)
    
    for i, trade in enumerate(data.get('active_trades', [])[:3]):
        print(f"\nTrade {i+1}:")
        print(f"  Trade ID: {trade.get('trade_id')}")
        print(f"  Direction: {trade.get('direction')}")
        print(f"  Entry: {trade.get('entry_price')}")
        print(f"  Status: {trade.get('status')}")
        print(f"  be_mfe: {trade.get('be_mfe')}")
        print(f"  no_be_mfe: {trade.get('no_be_mfe')}")
        print(f"  mfe: {trade.get('mfe')}")
        print(f"  final_mfe: {trade.get('final_mfe')}")
        print(f"  current_mfe: {trade.get('current_mfe')}")
        print(f"  All keys: {list(trade.keys())}")
    
    print("\n" + "="*80)
    print("COMPLETED TRADES (first 3):")
    print("="*80)
    
    for i, trade in enumerate(data.get('completed_trades', [])[:3]):
        print(f"\nTrade {i+1}:")
        print(f"  Trade ID: {trade.get('trade_id')}")
        print(f"  Direction: {trade.get('direction')}")
        print(f"  be_mfe: {trade.get('be_mfe')}")
        print(f"  no_be_mfe: {trade.get('no_be_mfe')}")
        
else:
    print(f"Error: {response.status_code}")
    print(response.text)
