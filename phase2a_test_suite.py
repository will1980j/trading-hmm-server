"""
PHASE 2A - COMPREHENSIVE TEST SUITE
Tests all webhook functionality with various payload formats
"""

import requests
import json
from datetime import datetime
import time

# Production URL
PRODUCTION_URL = "https://web-production-f8c3.up.railway.app"
WEBHOOK_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/webhook"
STATS_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/stats-live"

def get_current_count():
    """Get current signal count from stats endpoint"""
    try:
        response = requests.get(STATS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('stats', {}).get('total_signals', 0)
    except:
        pass
    return None

def test_webhook(test_name, payload, expected_status=200):
    """Test a webhook payload"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_ENDPOINT, json=payload, timeout=10)
        print(f"\n✓ Status Code: {response.status_code}")
        print(f"✓ Response: {response.text[:300]}")
        
        if response.status_code == expected_status:
            print(f"\n✅ PASS: Got expected status {expected_status}")
            return True
        else:
            print(f"\n❌ FAIL: Expected {expected_status}, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

print("=" * 80)
print("PHASE 2A - COMPREHENSIVE TEST SUITE")
print("=" * 80)
print(f"\nProduction URL: {PRODUCTION_URL}")
print(f"Webhook: {WEBHOOK_ENDPOINT}")
print(f"Stats: {STATS_ENDPOINT}")

# Get initial count
print("\n" + "=" * 80)
print("INITIAL STATE")
print("=" * 80)
initial_count = get_current_count()
if initial_count is not None:
    print(f"✓ Initial signal count: {initial_count}")
else:
    print("⚠️  Could not get initial count")

time.sleep(1)

# ============================================================================
# TEST 1: Direct Telemetry Format (ENTRY)
# ============================================================================
test1_passed = test_webhook(
    "Direct Telemetry Format - ENTRY",
    {
        "event_type": "ENTRY",
        "trade_id": f"TEST_DIRECT_ENTRY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "direction": "LONG",
        "entry_price": 21100.00,
        "stop_loss": 21075.00,
        "session": "NY AM",
        "bias": "Bullish",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    },
    expected_status=200
)

time.sleep(2)

# ============================================================================
# TEST 2: Strategy Format (signal_created)
# ============================================================================
test2_passed = test_webhook(
    "Strategy Format - signal_created",
    {
        "type": "signal_created",
        "signal_id": f"TEST_STRATEGY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "bias": "Bullish",
        "entry_price": 21150.00,
        "sl_price": 21125.00,
        "session": "NY AM"
    },
    expected_status=200
)

time.sleep(2)

# ============================================================================
# TEST 3: MFE_UPDATE Event
# ============================================================================
test3_passed = test_webhook(
    "Direct Telemetry Format - MFE_UPDATE",
    {
        "event_type": "MFE_UPDATE",
        "trade_id": f"TEST_MFE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "current_price": 21200.00,
        "mfe": 2.5,
        "be_mfe": 2.5,
        "no_be_mfe": 2.5
    },
    expected_status=200
)

time.sleep(2)

# ============================================================================
# TEST 4: Invalid Payload (Missing event_type)
# ============================================================================
test4_passed = test_webhook(
    "Invalid Payload - Missing event_type",
    {
        "trade_id": "TEST_INVALID_001",
        "entry_price": 21000.00
    },
    expected_status=400
)

time.sleep(2)

# ============================================================================
# TEST 5: Invalid Payload (Missing trade_id)
# ============================================================================
test5_passed = test_webhook(
    "Invalid Payload - Missing trade_id",
    {
        "event_type": "ENTRY",
        "entry_price": 21000.00,
        "stop_loss": 20975.00
    },
    expected_status=400
)

time.sleep(2)

# ============================================================================
# TEST 6: Invalid Payload (Invalid price)
# ============================================================================
test6_passed = test_webhook(
    "Invalid Payload - Invalid price",
    {
        "event_type": "ENTRY",
        "trade_id": "TEST_INVALID_PRICE",
        "entry_price": "not_a_number",
        "stop_loss": 20975.00
    },
    expected_status=400
)

time.sleep(2)

# ============================================================================
# VERIFICATION: Check if signals were stored
# ============================================================================
print("\n" + "=" * 80)
print("VERIFICATION - SIGNAL STORAGE")
print("=" * 80)

final_count = get_current_count()
if final_count is not None and initial_count is not None:
    added = final_count - initial_count
    print(f"\n✓ Initial count: {initial_count}")
    print(f"✓ Final count: {final_count}")
    print(f"✓ Signals added: {added}")
    
    # We expect 3 successful inserts (tests 1, 2, 3)
    # Test 3 might not insert if it's an MFE_UPDATE without prior ENTRY
    if added >= 2:
        print(f"\n✅ VERIFICATION PASSED: At least 2 signals were stored")
    else:
        print(f"\n⚠️  VERIFICATION WARNING: Expected at least 2 signals, got {added}")
else:
    print("\n⚠️  Could not verify signal storage")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

tests = [
    ("Direct Telemetry ENTRY", test1_passed),
    ("Strategy Format", test2_passed),
    ("MFE_UPDATE Event", test3_passed),
    ("Invalid - Missing event_type", test4_passed),
    ("Invalid - Missing trade_id", test5_passed),
    ("Invalid - Bad price", test6_passed)
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

print(f"\nResults: {passed}/{total} tests passed\n")

for test_name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")

if passed == total:
    print(f"\n{'='*80}")
    print("🎉 ALL TESTS PASSED!")
    print(f"{'='*80}")
    print("\nThe webhook handler is working correctly.")
    print("Ready for production deployment.")
else:
    print(f"\n{'='*80}")
    print(f"⚠️  {total - passed} TEST(S) FAILED")
    print(f"{'='*80}")
    print("\nReview the failed tests above and fix any issues.")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
1. If all tests passed:
   - Commit changes to GitHub
   - Push to main branch
   - Railway will auto-deploy
   - Monitor Railway logs

2. If tests failed:
   - Review error messages above
   - Check web_server.py for issues
   - Re-run tests after fixes

3. Production verification:
   - Test with actual TradingView webhook
   - Monitor /api/automated-signals/stats-live
   - Check dashboard for new signals
""")
