"""
Check Export Status - Diagnose what's happening
"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("EXPORT STATUS DIAGNOSIS")
print("=" * 80)
print()

# Check 1: Is inspector endpoint receiving data?
print("1. Checking Inspector Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            total = data.get('total_signals', 0)
            if total > 0:
                print(f"   ✅ Inspector has received {total} signals!")
            else:
                print(f"   ⚠️ Inspector endpoint exists but no signals received yet")
        else:
            print(f"   ⚠️ Inspector returned success=false")
    else:
        print(f"   ❌ Inspector endpoint returned {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Check 2: Test webhook endpoint directly
print("2. Testing Webhook Endpoint...")
try:
    test_payload = {
        "event_type": "INDICATOR_EXPORT",
        "batch_number": 0,
        "total_signals": 1,
        "signals": [{
            "trade_id": "20251214_120000000_BULLISH",
            "date": "2025-12-14",
            "direction": "Bullish",
            "entry": 21000.0,
            "stop": 20975.0,
            "be_mfe": 2.5,
            "no_be_mfe": 3.0,
            "mae": -0.5,
            "completed": False
        }]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/indicator-inspector/receive",
        json=test_payload
    )
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print(f"   ✅ Webhook endpoint is working!")
    else:
        print(f"   ❌ Webhook endpoint returned {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Check 3: Verify alert is configured correctly
print("3. Alert Configuration Checklist:")
print("   ⚠️ MANUAL CHECK REQUIRED:")
print()
print("   In TradingView, verify:")
print("   [ ] Alert exists named 'Indicator Export' or similar")
print("   [ ] Condition: NQ_FVG_CORE_TELEMETRY_V1")
print("   [ ] Message: {{strategy.order.alert_message}}")
print(f"   [ ] Webhook URL: {BASE_URL}/api/indicator-inspector/receive")
print("   [ ] Frequency: Once Per Bar Close")
print()

# Check 4: Verify indicator settings
print("4. Indicator Settings Checklist:")
print("   ⚠️ MANUAL CHECK REQUIRED:")
print()
print("   In TradingView indicator settings, verify:")
print("   [ ] 'Export' section exists")
print("   [ ] '📤 Enable Bulk Export' is CHECKED")
print("   [ ] 'Delay Between Batches' is set to 0")
print("   [ ] Settings have been APPLIED (clicked OK)")
print()

# Check 5: Check if indicator is on a live chart
print("5. Chart Status Checklist:")
print("   ⚠️ MANUAL CHECK REQUIRED:")
print()
print("   Verify:")
print("   [ ] Chart is OPEN in TradingView")
print("   [ ] Indicator is LOADED on chart")
print("   [ ] Chart is receiving live data (bars updating)")
print("   [ ] Indicator display panel shows export progress")
print()

print("=" * 80)
print("TROUBLESHOOTING STEPS")
print("=" * 80)
print()
print("If export is not working:")
print()
print("1. Check indicator display panel on chart")
print("   - Should show: 📤 EXPORT: Batch X/107")
print("   - If not showing, export is not enabled")
print()
print("2. Verify ENABLE_EXPORT is checked")
print("   - Open indicator settings")
print("   - Find 'Export' section")
print("   - Check ✅ Enable Bulk Export")
print("   - Click OK to apply")
print()
print("3. Verify alert exists and is active")
print("   - TradingView → Alerts tab")
print("   - Should see 'Indicator Export' alert")
print("   - Status should be 'Active'")
print()
print("4. Check Railway logs for webhook reception")
print("   - Railway dashboard → Logs")
print("   - Look for 'INDICATOR_EXPORT' messages")
print()
print("5. Try manual test:")
print("   - Run this script again")
print("   - Check if test payload was received")
print("   - If yes, webhook works but indicator not sending")
print()
