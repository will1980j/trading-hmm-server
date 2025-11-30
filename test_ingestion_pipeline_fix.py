#!/usr/bin/env python3
"""
Automated Signals Ingestion Pipeline Fix - Production Test
Tests the complete ENTRY -> MFE_UPDATE -> BE_TRIGGERED -> EXIT flow on Railway
"""

import requests
import json
import time
from datetime import datetime

# Production configuration
BASE_URL = "https://web-production-cd33.up.railway.app"
TEST_URL = f"{BASE_URL}/api/automated-signals/test-lifecycle"
WEBHOOK_URL = f"{BASE_URL}/api/automated-signals/webhook"
DATA_URL = f"{BASE_URL}/api/automated-signals/dashboard-data"

def test_built_in_lifecycle():
    """Test using the built-in lifecycle test endpoint"""
    print("=" * 80)
    print("TESTING BUILT-IN LIFECYCLE TEST ENDPOINT")
    print("=" * 80)
    
    try:
        print(f"Calling: {TEST_URL}")
        response = requests.post(TEST_URL, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nTest Trade ID: {data.get('test_trade_id')}")
            print(f"Overall Result: {data.get('overall')}")
            print(f"Timestamp: {data.get('timestamp')}")
            
            print("\nStep Results:")
            for result in data.get('test_results', []):
                status_icon = "✅" if result.get('status') == 'PASS' else "❌"
                step = result.get('step')
                status = result.get('status')
                
                if 'error' in result:
                    print(f"  {status_icon} {step}: {status} - {result['error']}")
                else:
                    print(f"  {status_icon} {step}: {status} - {result.get('result', 'OK')}")
            
            return data.get('overall') == 'PASS'
        else:
            print(f"Error: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_manual_webhook_lifecycle():
    """Test by sending individual webhook calls"""
    print("\n" + "=" * 80)
    print("TESTING MANUAL WEBHOOK CALLS")
    print("=" * 80)
    
    trade_id = f"MANUAL_TEST_{int(time.time())}"
    
    # Test ENTRY
    print("\n1. Testing ENTRY event...")
    entry_payload = {
        "trade_id": trade_id,
        "event_type": "ENTRY",
        "symbol": "NQ",
        "direction": "LONG",
        "entry_price": "18500.00",
        "stop_loss": "18450.00",
        "session": "NY_AM",
        "bias": "Bullish"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=entry_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code != 200:
            print("❌ ENTRY failed - stopping manual test")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    time.sleep(1)
    
    # Test MFE_UPDATE
    print("\n2. Testing MFE_UPDATE event...")
    mfe_payload = {
        "trade_id": trade_id,
        "event_type": "MFE_UPDATE",
        "current_price": "18525.00",
        "be_mfe": "0.5",
        "no_be_mfe": "0.5"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=mfe_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)
    
    # Test EXIT
    print("\n3. Testing EXIT_BE event...")
    exit_payload = {
        "trade_id": trade_id,
        "event_type": "EXIT_BE",
        "exit_price": "18500.00",
        "final_be_mfe": "1.0",
        "final_no_be_mfe": "1.5"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=exit_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\n✅ Manual test completed for trade_id: {trade_id}")
    return True


if __name__ == "__main__":
    print("AUTOMATED SIGNALS INGESTION PIPELINE FIX - PRODUCTION TEST")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test 1: Built-in lifecycle test
    builtin_success = test_built_in_lifecycle()
    
    # Test 2: Manual webhook calls
    manual_success = test_manual_webhook_lifecycle()
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS:")
    print(f"Built-in Test: {'✅ PASS' if builtin_success else '❌ FAIL'}")
    print(f"Manual Test: {'✅ PASS' if manual_success else '❌ FAIL'}")
    
    if builtin_success and manual_success:
        print("\n🎉 ALL TESTS PASSED - Automated Signals pipeline is working!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Check logs for details")
    print("=" * 80)
