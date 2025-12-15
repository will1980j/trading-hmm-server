"""
Check if Export is Actually Running
Even if you can't see progress, check if data is arriving
"""

import requests
import time

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("CHECKING IF EXPORT IS RUNNING (EVEN IF INVISIBLE)")
print("=" * 80)
print()

print("Monitoring inspector endpoint for 30 seconds...")
print("If export is running, signals should start appearing...")
print()

initial_count = 0
try:
    response = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
    if response.status_code == 200:
        data = response.json()
        initial_count = data.get('total_signals', 0)
        print(f"Initial count: {initial_count} signals")
except:
    print("Could not get initial count")

print()
print("Waiting 30 seconds for new signals...")
print("(Each bar close should send a batch if export is enabled)")
print()

for i in range(6):
    time.sleep(5)
    try:
        response = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
        if response.status_code == 200:
            data = response.json()
            current_count = data.get('total_signals', 0)
            
            if current_count > initial_count:
                print(f"✅ EXPORT IS RUNNING! Received {current_count} signals (+{current_count - initial_count})")
                print()
                print("Export is working but progress display is hidden!")
                print("To see progress:")
                print("1. Open indicator settings")
                print("2. Check ✅ 'Show Position Sizing Table'")
                print("3. Look for export progress at bottom of position table")
                exit(0)
            else:
                print(f"   {(i+1)*5}s: Still {current_count} signals (no change)")
    except Exception as e:
        print(f"   {(i+1)*5}s: Error checking: {e}")

print()
print("=" * 80)
print("NO NEW SIGNALS RECEIVED")
print("=" * 80)
print()
print("Export is NOT running. Possible causes:")
print()
print("1. ENABLE_EXPORT is not checked")
print("   → Open indicator settings → Export section")
print("   → Check ✅ 'Enable Bulk Export'")
print("   → Click OK")
print()
print("2. Alert is not configured")
print("   → TradingView → Alerts tab")
print("   → Should see 'Indicator Export' alert")
print("   → Verify webhook URL is correct")
print()
print("3. Chart is not receiving live data")
print("   → Verify chart is open and updating")
print("   → Indicator must be loaded on chart")
print("   → Bars must be closing (1m chart = 1 bar per minute)")
print()
print("4. Export already completed")
print("   → Check if export_complete flag is set")
print("   → May need to change ARRAY_VERSION to reset")
print()
