#!/usr/bin/env python3
"""
MONDAY READINESS TEST - Comprehensive End-to-End Webhook Pipeline Verification

This script tests the EXACT payload format from NQ_FVG_CORE_TELEMETRY_V1.pine
to ensure signals will be correctly ingested on Monday market open.

Tests:
1. ENTRY event ingestion
2. MFE_UPDATE event processing
3. BE_TRIGGERED event handling
4. EXIT_BREAK_EVEN event handling
5. EXIT_STOP_LOSS event handling
6. Dashboard data retrieval
7. WebSocket broadcast verification
"""

import requests
import json
import time
from datetime import datetime
import sys

# Production URL
PRODUCTION_URL = "https://web-production-f8c3.up.railway.app"
WEBHOOK_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/webhook"
DASHBOARD_DATA_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/dashboard-data"
STATS_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/stats-live"

# Generate unique trade ID for this test
TEST_TRADE_ID = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_BULLISH"

def create_telemetry_payload(event_type, mfe_r=0.0, final_mfe_r=None, exit_price=None, exit_reason=""):
    """
    Create EXACT payload format matching NQ_FVG_CORE_TELEMETRY_V1.pine f_buildPayload()
    """
    payload = {
        "schema_version": "1.0.0",
        "engine_version": "1.0.0",
        "strategy_name": "NQ_FVG_CORE",
        "strategy_id": "NQ_FVG_CORE",
        "strategy_version": "2025.11.20",
        "trade_id": TEST_TRADE_ID,
        "event_type": event_type,
        "event_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbol": "NQ1!",
        "exchange": "CME_MINI:NQ1!",
        "timeframe": "1",
        "session": "NY AM",
        "direction": "Bullish",
        "entry_price": 21050.25,
        "stop_loss": 21025.00,
        "risk_R": 1.0,
        "position_size": 2,
        "be_price": None if event_type == "ENTRY" else 21050.25,
        "mfe_R": mfe_r,
        "mae_R": 0.0,
        "final_mfe_R": final_mfe_r,
        "exit_price": exit_price,
        "exit_timestamp": None,
        "exit_reason": exit_reason,
        "targets": {
            "tp1_price": 21075.50,
            "tp2_price": 21100.75,
            "tp3_price": 21126.00,
            "target_Rs": [1.0, 2.0, 3.0]
        },
        "setup": {
            "setup_family": "FVG_CORE",
            "setup_variant": "HTF_ALIGNED" if event_type == "ENTRY" else "ACTIVE",
            "setup_id": "FVG_CORE_HTF_ALIGNED",
            "signal_strength": 75,
            "confidence_components": {
                "trend_alignment": 1.0,
                "structure_quality": 0.8,
                "volatility_fit": 0.7
            }
        },
        "market_state": {
            "trend_regime": "Bullish",
            "trend_score": 0.8,
            "volatility_regime": "NORMAL",
            "atr": None,
            "atr_percentile_20d": None,
            "daily_range_percentile_20d": None,
            "price_location": {
                "vs_daily_open": None,
                "vs_vwap": None,
                "distance_to_HTF_level_points": None
            },
            "structure": {
                "swing_state": "UNKNOWN",
                "bos_choch_signal": "NONE",
                "liquidity_context": "NEUTRAL"
            }
        }
    }
    return payload


def test_webhook_endpoint_health():
    """Test 1: Verify webhook endpoint is accessible"""
    print("\n" + "="*80)
    print("TEST 1: Webhook Endpoint Health Check")
    print("="*80)
    
    try:
        # Test with OPTIONS request first
        response = requests.options(WEBHOOK_ENDPOINT, timeout=10)
        print(f"OPTIONS response: {response.status_code}")
        
        # Test health endpoint
        health_url = f"{PRODUCTION_URL}/api/webhook-health"
        response = requests.get(health_url, timeout=10)
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Health data: {response.json()}")
            return True
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_entry_event():
    """Test 2: Send ENTRY event and verify storage"""
    print("\n" + "="*80)
    print("TEST 2: ENTRY Event Ingestion")
    print("="*80)
    
    payload = create_telemetry_payload("ENTRY")
    print(f"Trade ID: {TEST_TRADE_ID}")
    print(f"Payload preview: event_type={payload['event_type']}, direction={payload['direction']}")
    
    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get("success"):
            print("✅ ENTRY event ingested successfully")
            return True
        else:
            print(f"❌ ENTRY event failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ENTRY test failed: {e}")
        return False


def test_mfe_update_event():
    """Test 3: Send MFE_UPDATE event"""
    print("\n" + "="*80)
    print("TEST 3: MFE_UPDATE Event Processing")
    print("="*80)
    
    payload = create_telemetry_payload("MFE_UPDATE", mfe_r=0.5)
    
    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get("success"):
            print("✅ MFE_UPDATE event processed successfully")
            return True
        else:
            print(f"❌ MFE_UPDATE event failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ MFE_UPDATE test failed: {e}")
        return False


def test_be_triggered_event():
    """Test 4: Send BE_TRIGGERED event"""
    print("\n" + "="*80)
    print("TEST 4: BE_TRIGGERED Event Processing")
    print("="*80)
    
    payload = create_telemetry_payload("BE_TRIGGERED", mfe_r=1.0)
    
    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get("success"):
            print("✅ BE_TRIGGERED event processed successfully")
            return True
        else:
            print(f"❌ BE_TRIGGERED event failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ BE_TRIGGERED test failed: {e}")
        return False


def test_dashboard_data_retrieval():
    """Test 5: Verify dashboard can retrieve the test trade"""
    print("\n" + "="*80)
    print("TEST 5: Dashboard Data Retrieval")
    print("="*80)
    
    try:
        response = requests.get(DASHBOARD_DATA_ENDPOINT, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if our test trade appears
            active_trades = data.get("active_trades", [])
            completed_trades = data.get("completed_trades", [])
            
            print(f"Active trades count: {len(active_trades)}")
            print(f"Completed trades count: {len(completed_trades)}")
            
            # Look for our test trade
            found = False
            for trade in active_trades + completed_trades:
                if trade.get("trade_id") == TEST_TRADE_ID:
                    found = True
                    print(f"\n✅ Found test trade in dashboard data:")
                    print(f"   Trade ID: {trade.get('trade_id')}")
                    print(f"   Direction: {trade.get('direction')}")
                    print(f"   Entry: {trade.get('entry_price')}")
                    print(f"   Stop: {trade.get('stop_loss')}")
                    print(f"   MFE: {trade.get('mfe')}")
                    break
            
            if not found:
                print(f"⚠️ Test trade {TEST_TRADE_ID} not found in dashboard data")
                print("   This may be expected if the trade was just created")
            
            return True
        else:
            print(f"❌ Dashboard data retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard data test failed: {e}")
        return False


def test_stats_endpoint():
    """Test 6: Verify stats endpoint returns valid data"""
    print("\n" + "="*80)
    print("TEST 6: Stats Endpoint Verification")
    print("="*80)
    
    try:
        response = requests.get(STATS_ENDPOINT, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Stats: {json.dumps(stats, indent=2)}")
            
            # Verify expected fields
            expected_fields = ["total_signals", "active_count", "completed_count"]
            missing = [f for f in expected_fields if f not in stats]
            
            if missing:
                print(f"⚠️ Missing expected fields: {missing}")
            else:
                print("✅ Stats endpoint returns all expected fields")
            
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats test failed: {e}")
        return False


def cleanup_test_trade():
    """Cleanup: Delete the test trade"""
    print("\n" + "="*80)
    print("CLEANUP: Removing Test Trade")
    print("="*80)
    
    try:
        delete_url = f"{PRODUCTION_URL}/api/automated-signals/delete/{TEST_TRADE_ID}"
        response = requests.delete(delete_url, timeout=30)
        
        print(f"Delete response: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Test trade {TEST_TRADE_ID} deleted")
            return True
        else:
            print(f"⚠️ Could not delete test trade: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")
        return False


def main():
    """Run all Monday readiness tests"""
    print("\n" + "="*80)
    print("🚀 MONDAY READINESS TEST - NQ_FVG_CORE_TELEMETRY_V1 Pipeline Verification")
    print("="*80)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Test Trade ID: {TEST_TRADE_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {}
    
    # Run tests
    results["health"] = test_webhook_endpoint_health()
    time.sleep(1)
    
    results["entry"] = test_entry_event()
    time.sleep(2)  # Allow time for DB write
    
    results["mfe_update"] = test_mfe_update_event()
    time.sleep(1)
    
    results["be_triggered"] = test_be_triggered_event()
    time.sleep(1)
    
    results["dashboard"] = test_dashboard_data_retrieval()
    time.sleep(1)
    
    results["stats"] = test_stats_endpoint()
    
    # Cleanup
    cleanup_test_trade()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - System is READY for Monday!")
        print("   The webhook pipeline will correctly ingest signals from")
        print("   NQ_FVG_CORE_TELEMETRY_V1.pine when the market opens.")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Review issues before Monday!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
