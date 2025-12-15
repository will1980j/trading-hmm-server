"""
Check what signals have been exported
"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("Checking exported signals...")
print()

try:
    response = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
    data = response.json()
    
    print(f"Total Signals: {data.get('total_signals', 0)}")
    print(f"Active: {data.get('active', 0)}")
    print(f"Completed: {data.get('completed', 0)}")
    print()
    
    if data.get('total_signals', 0) > 0:
        print("Sample signals:")
        for i, sig in enumerate(data.get('sample_signals', [])[:3], 1):
            print(f"\n{i}. {sig.get('trade_id', 'N/A')}")
            print(f"   Date: {sig.get('date', 'N/A')}")
            print(f"   Direction: {sig.get('direction', 'N/A')}")
            print(f"   Entry: ${sig.get('entry', 'N/A')}")
            print(f"   Stop: ${sig.get('stop', 'N/A')}")
            print(f"   BE MFE: {sig.get('be_mfe', 'N/A')}R")
            print(f"   No-BE MFE: {sig.get('no_be_mfe', 'N/A')}R")
            print(f"   MAE: {sig.get('mae', 'N/A')}R")
            print(f"   Completed: {sig.get('completed', False)}")
    
except Exception as e:
    print(f"Error: {e}")
