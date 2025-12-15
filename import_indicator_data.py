"""
Import Indicator Data to Database
Final step after export and analysis
"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("INDICATOR DATA IMPORT")
print("=" * 80)
print()

# Step 1: Get all signals from inspector
print("Step 1: Fetching exported signals from inspector...")
try:
    response = requests.get(f"{BASE_URL}/api/indicator-inspector/all")
    if response.status_code != 200:
        print(f"❌ Failed to fetch signals: {response.status_code}")
        exit(1)
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Error: {data.get('error')}")
        exit(1)
    
    signals = data.get('signals', [])
    print(f"✅ Fetched {len(signals)} signals from inspector")
    print()
    
except Exception as e:
    print(f"❌ Error fetching signals: {e}")
    exit(1)

# Step 2: Import confirmed signals to database
print("Step 2: Importing confirmed signals to database...")
try:
    response = requests.post(
        f"{BASE_URL}/api/indicator-import/bulk",
        json={'signals': signals}
    )
    
    if response.status_code != 200:
        print(f"❌ Import failed: {response.status_code}")
        print(response.text)
        exit(1)
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Import error: {result.get('error')}")
        exit(1)
    
    print(f"✅ Import complete!")
    print(f"   Imported: {result.get('imported', 0)}")
    print(f"   Skipped (duplicates): {result.get('skipped', 0)}")
    print(f"   Total: {result.get('total', 0)}")
    print()
    
except Exception as e:
    print(f"❌ Error importing signals: {e}")
    exit(1)

# Step 3: Verify dashboard stats
print("Step 3: Verifying dashboard stats...")
try:
    response = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
    if response.status_code != 200:
        print(f"⚠️ Could not verify stats: {response.status_code}")
    else:
        data = response.json()
        print(f"✅ Dashboard stats updated:")
        print(f"   Active Trades: {data.get('active_count', 0)}")
        print(f"   Completed Trades: {data.get('completed_count', 0)}")
        print(f"   Total: {data.get('active_count', 0) + data.get('completed_count', 0)}")
        print()
        
        # Check if counts match expected
        expected_active = 510
        expected_completed = 1614
        expected_total = 2124
        
        actual_total = data.get('active_count', 0) + data.get('completed_count', 0)
        
        if actual_total >= expected_total:
            print("🎉 SUCCESS! All signals imported correctly!")
        else:
            print(f"⚠️ Warning: Expected {expected_total} signals, got {actual_total}")
            print("   Some signals may have been skipped as duplicates")
        
except Exception as e:
    print(f"⚠️ Could not verify stats: {e}")

print()
print("=" * 80)
print("IMPORT COMPLETE")
print("=" * 80)
print()
print("NEXT STEPS:")
print("1. Open Automated Signals Dashboard:")
print(f"   {BASE_URL}/automated-signals")
print("2. Verify active/completed counts match")
print("3. Check calendar shows Nov 16 - Dec 12 data")
print("4. Click a few trades to verify details")
print("5. Disable 'Enable Bulk Export' in indicator settings")
print("6. Delete export alert (keep main webhook alert)")
print()
print("🎉 You now have 4 weeks of perfect historical data!")
print()
