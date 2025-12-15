"""
Check if All Signals export data exists
"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

# The inspector stores everything together
# Need to check if there are signals with ALL_SIGNALS_EXPORT event type

r = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
data = r.json()

print(f"Total signals in inspector: {data.get('total_signals', 0)}")
print()

# Check a few samples to see format
if data.get('sample_signals'):
    print("Sample signal format:")
    print(json.dumps(data['sample_signals'][0], indent=2))
    print()
    
    # Check if any have All Signals specific fields
    has_htf = any('htf_daily' in s for s in data['sample_signals'])
    has_status = any('status' in s for s in data['sample_signals'])
    
    print(f"Has HTF fields: {has_htf}")
    print(f"Has status field: {has_status}")
    print()
    
    if has_htf or has_status:
        print("✅ All Signals data IS being exported!")
    else:
        print("❌ All Signals data NOT found - only Confirmed Signals")
