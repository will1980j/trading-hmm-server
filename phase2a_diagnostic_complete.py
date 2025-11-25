"""
PHASE 2A - COMPLETE DIAGNOSTIC
Comprehensive analysis of Automated Signals ingestion pipeline
"""

import requests
import json
from datetime import datetime

# CRITICAL: Updated production URL per prompt
PRODUCTION_URL = "https://web-production-f8c3.up.railway.app"
WEBHOOK_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/webhook"
STATS_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/stats-live"

print("=" * 80)
print("PHASE 2A - AUTOMATED SIGNALS INGESTION DIAGNOSTIC")
print("=" * 80)
print(f"\nProduction URL: {PRODUCTION_URL}")
print(f"Webhook Endpoint: {WEBHOOK_ENDPOINT}")
print(f"Stats Endpoint: {STATS_ENDPOINT}")
print()

# ============================================================================
# TEST 1: Check if webhook endpoint is accessible
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: WEBHOOK ENDPOINT ACCESSIBILITY")
print("=" * 80)

try:
    # Send a minimal test payload
    test_payload = {
        "event_type": "ENTRY",
        "trade_id": f"DIAGNOSTIC_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "direction": "LONG",
        "entry_price": 21000.00,
        "stop_loss": 20975.00,
        "session": "NY AM",
        "bias": "Bullish"
    }
    
    print(f"\nSending test webhook...")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    response = requests.post(
        WEBHOOK_ENDPOINT,
        json=test_payload,
        timeout=10
    )
    
    print(f"\n✓ Response Status: {response.status_code}")
    print(f"✓ Response Body: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ WEBHOOK ENDPOINT IS ACCESSIBLE")
    else:
        print(f"\n❌ WEBHOOK RETURNED ERROR: {response.status_code}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ CONNECTION ERROR: Cannot reach {WEBHOOK_ENDPOINT}")
    print(f"   Error: {str(e)}")
except requests.exceptions.Timeout:
    print(f"\n❌ TIMEOUT: Webhook took too long to respond")
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")

# ============================================================================
# TEST 2: Check stats endpoint
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: STATS ENDPOINT CHECK")
print("=" * 80)

try:
    print(f"\nFetching stats from: {STATS_ENDPOINT}")
    
    response = requests.get(STATS_ENDPOINT, timeout=10)
    
    print(f"\n✓ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Response Data:")
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            stats = data.get('stats', {})
            print(f"\n📊 CURRENT STATS:")
            print(f"   Total Signals: {stats.get('total_signals', 0)}")
            print(f"   Active Trades: {stats.get('active_count', 0)}")
            print(f"   Completed Trades: {stats.get('completed_count', 0)}")
            
            if stats.get('total_signals', 0) == 0:
                print(f"\n⚠️  NO SIGNALS IN DATABASE")
            else:
                print(f"\n✅ DATABASE HAS {stats.get('total_signals')} SIGNALS")
        else:
            print(f"\n❌ STATS ENDPOINT RETURNED success=false")
    else:
        print(f"\n❌ STATS ENDPOINT ERROR: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ STATS CHECK FAILED: {type(e).__name__}: {str(e)}")

# ============================================================================
# TEST 3: Send complete test signal and verify storage
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: END-TO-END SIGNAL STORAGE TEST")
print("=" * 80)

try:
    # Get initial count
    print("\n1. Getting initial signal count...")
    initial_response = requests.get(STATS_ENDPOINT, timeout=10)
    initial_count = 0
    
    if initial_response.status_code == 200:
        initial_data = initial_response.json()
        if initial_data.get('success'):
            initial_count = initial_data.get('stats', {}).get('total_signals', 0)
            print(f"   Initial count: {initial_count}")
    
    # Send test signal
    print("\n2. Sending test ENTRY signal...")
    test_trade_id = f"E2E_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    entry_payload = {
        "event_type": "ENTRY",
        "trade_id": test_trade_id,
        "direction": "LONG",
        "entry_price": 21050.00,
        "stop_loss": 21025.00,
        "risk_distance": 25.00,
        "session": "NY AM",
        "bias": "Bullish",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S")
    }
    
    print(f"   Trade ID: {test_trade_id}")
    
    webhook_response = requests.post(
        WEBHOOK_ENDPOINT,
        json=entry_payload,
        timeout=10
    )
    
    print(f"   Webhook Status: {webhook_response.status_code}")
    print(f"   Webhook Response: {webhook_response.text[:200]}")
    
    # Wait a moment for database write
    import time
    time.sleep(2)
    
    # Check if count increased
    print("\n3. Verifying signal was stored...")
    final_response = requests.get(STATS_ENDPOINT, timeout=10)
    
    if final_response.status_code == 200:
        final_data = final_response.json()
        if final_data.get('success'):
            final_count = final_data.get('stats', {}).get('total_signals', 0)
            print(f"   Final count: {final_count}")
            
            if final_count > initial_count:
                print(f"\n✅ SUCCESS: Signal was stored! Count increased from {initial_count} to {final_count}")
            else:
                print(f"\n❌ FAILURE: Signal was NOT stored. Count remained at {initial_count}")
                print(f"\n🔍 DIAGNOSIS: Webhook accepted signal but database insert failed")
        else:
            print(f"\n❌ Stats endpoint returned success=false")
    else:
        print(f"\n❌ Could not verify storage (stats endpoint error)")
        
except Exception as e:
    print(f"\n❌ END-TO-END TEST FAILED: {type(e).__name__}: {str(e)}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)
print(f"""
Next Steps:
1. Review the test results above
2. If webhook is not accessible, check Railway deployment
3. If webhook accepts but doesn't store, check database connection
4. If stats endpoint fails, check DATABASE_URL environment variable
5. Check Railway logs for detailed error messages

Production URLs:
- Webhook: {WEBHOOK_ENDPOINT}
- Stats: {STATS_ENDPOINT}
- Dashboard: {PRODUCTION_URL}/automated-signals-dashboard
""")
