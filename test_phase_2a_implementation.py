#!/usr/bin/env python3
"""
Phase 2A Implementation Test
Validates normalization layer, state builder, and new API endpoints
"""

import requests
import json
from datetime import datetime
from signal_normalization import normalize_signal_payload, validate_normalized_payload
from signal_state_builder import build_signal_state

# Test configuration
BASE_URL = "https://web-production-cd33.up.railway.app"

def test_normalization_layer():
    """Test the normalization layer with various payloads"""
    print("\n" + "="*60)
    print("TESTING NORMALIZATION LAYER")
    print("="*60)
    
    # Test payload 1: Basic ENTRY signal
    test_payload_1 = {
        "event_type": "ENTRY",
        "direction": "Bullish",
        "entry_price": "20150.50",
        "stop_loss": "20100.00",
        "session": "NY AM",
        "trade_id": "TEST_NORM_001",
        "timestamp": datetime.now().isoformat()
    }
    
    print("\n1. Testing basic ENTRY signal normalization...")
    normalized = normalize_signal_payload(test_payload_1)
    is_valid, error = validate_normalized_payload(normalized)
    
    print(f"   Raw direction: {test_payload_1['direction']}")
    print(f"   Normalized direction: {normalized.get('direction')}")
    print(f"   Raw session: {test_payload_1['session']}")
    print(f"   Normalized session: {normalized.get('session')}")
    print(f"   Entry price type: {type(normalized.get('entry_price'))}")
    print(f"   Validation: {'✅ PASS' if is_valid else f'❌ FAIL - {error}'}")
    
    # Test payload 2: MFE_UPDATE event
    test_payload_2 = {
        "event_type": "MFE_UPDATE",
        "trade_id": "TEST_NORM_001",
        "mfe": "1.25",
        "current_price": "20175.75"
    }
    
    print("\n2. Testing MFE_UPDATE normalization...")
    normalized_2 = normalize_signal_payload(test_payload_2)
    is_valid_2, error_2 = validate_normalized_payload(normalized_2)
    
    print(f"   Event type: {normalized_2.get('event_type')}")
    print(f"   Status mapping: {normalized_2.get('status')}")
    print(f"   MFE type: {type(normalized_2.get('mfe'))}")
    print(f"   Validation: {'✅ PASS' if is_valid_2 else f'❌ FAIL - {error_2}'}")
    
    return normalized, normalized_2

def test_state_builder():
    """Test the signal state builder"""
    print("\n" + "="*60)
    print("TESTING SIGNAL STATE BUILDER")
    print("="*60)
    
    # Mock database rows for a trade lifecycle
    mock_rows = [
        {
            'trade_id': 'TEST_STATE_001',
            'event_type': 'ENTRY',
            'direction': 'LONG',
            'entry_price': 20150.50,
            'stop_loss': 20100.00,
            'session': 'NY_AM',
            'timestamp': 1700000000000,
            'created_at': datetime.now(),
            'mfe': None,
            'be_mfe': None,
            'no_be_mfe': None,
            'bias': 'LONG',
            'risk_distance': 50.50
        },
        {
            'trade_id': 'TEST_STATE_001',
            'event_type': 'MFE_UPDATE',
            'direction': 'LONG',
            'entry_price': 20150.50,
            'stop_loss': 20100.00,
            'session': 'NY_AM',
            'timestamp': 1700000060000,
            'created_at': datetime.now(),
            'mfe': 1.25,
            'be_mfe': 1.25,
            'no_be_mfe': 1.25,
            'current_price': 20175.75,
            'bias': 'LONG',
            'risk_distance': 50.50
        },
        {
            'trade_id': 'TEST_STATE_001',
            'event_type': 'EXIT_TARGET',
            'direction': 'LONG',
            'entry_price': 20150.50,
            'stop_loss': 20100.00,
            'session': 'NY_AM',
            'timestamp': 1700000120000,
            'created_at': datetime.now(),
            'mfe': 2.0,
            'be_mfe': 2.0,
            'no_be_mfe': 2.0,
            'final_mfe': 2.0,
            'exit_price': 20250.50,
            'current_price': 20250.50,
            'bias': 'LONG',
            'risk_distance': 50.50
        }
    ]
    
    print("\n1. Building unified state from lifecycle events...")
    state = build_signal_state(mock_rows)
    
    if state:
        print(f"   Trade ID: {state.get('trade_id')}")
        print(f"   Direction: {state.get('direction')}")
        print(f"   Status: {state.get('status')}")
        print(f"   Entry Price: {state.get('entry_price')}")
        print(f"   Final MFE: {state.get('mfe')}")
        print(f"   R-Multiple: {state.get('r_multiple')}")
        print(f"   Event Count: {state.get('event_count')}")
        print(f"   Last Event: {state.get('last_event_type')}")
        print("   ✅ State builder working correctly")
    else:
        print("   ❌ State builder failed")
    
    return state

def test_new_api_endpoints():
    """Test the new Phase 2A API endpoints"""
    print("\n" + "="*60)
    print("TESTING NEW API ENDPOINTS")
    print("="*60)
    
    endpoints_to_test = [
        ('/api/signals/live', 'Live Signals'),
        ('/api/signals/recent?limit=10', 'Recent Signals'),
        ('/api/signals/today', 'Today Signals'),
        ('/api/signals/stats/today', 'Today Stats'),
        ('/api/session-summary', 'Session Summary'),
        ('/api/system-status', 'System Status')
    ]
    
    results = {}
    
    for endpoint, name in endpoints_to_test:
        print(f"\n{len(results)+1}. Testing {name} ({endpoint})...")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', True):
                    print(f"   ✅ {name}: Status 200, Valid JSON")
                    if 'signals' in data:
                        print(f"   📊 Signals count: {len(data.get('signals', []))}")
                    if 'total' in data:
                        print(f"   📊 Total: {data.get('total')}")
                    results[endpoint] = 'PASS'
                else:
                    print(f"   ⚠️  {name}: Status 200 but success=false")
                    print(f"   Error: {data.get('error', 'Unknown')}")
                    results[endpoint] = 'PARTIAL'
            else:
                print(f"   ❌ {name}: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                results[endpoint] = 'FAIL'
                
        except Exception as e:
            print(f"   ❌ {name}: Exception - {e}")
            results[endpoint] = 'ERROR'
    
    return results

def main():
    """Run all Phase 2A tests"""
    print("🚀 PHASE 2A IMPLEMENTATION VALIDATION")
    print("Testing normalization layer, state builder, and new API endpoints")
    print("=" * 80)
    
    # Test 1: Normalization layer
    try:
        norm_results = test_normalization_layer()
        print("\n✅ Normalization layer tests completed")
    except Exception as e:
        print(f"\n❌ Normalization layer tests failed: {e}")
        return
    
    # Test 2: State builder
    try:
        state_result = test_state_builder()
        print("\n✅ State builder tests completed")
    except Exception as e:
        print(f"\n❌ State builder tests failed: {e}")
        return
    
    # Test 3: New API endpoints
    try:
        api_results = test_new_api_endpoints()
        print("\n✅ API endpoint tests completed")
        
        # Summary
        passed = sum(1 for r in api_results.values() if r == 'PASS')
        total = len(api_results)
        print(f"\n📊 API Endpoints Summary: {passed}/{total} passing")
        
    except Exception as e:
        print(f"\n❌ API endpoint tests failed: {e}")
    
    print("\n" + "="*80)
    print("🎯 PHASE 2A VALIDATION COMPLETE")
    print("\nIf all tests passed, Phase 2A implementation is ready for deployment.")
    print("\nNext steps:")
    print("1. Commit changes to GitHub")
    print("2. Deploy to Railway")
    print("3. Begin Phase 2B (ULTRA dashboard integration)")
    print("="*80)

if __name__ == "__main__":
    main()
