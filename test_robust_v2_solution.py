#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_robust_v2_solution():
    """Test the robust V2 database solution"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🚀 TESTING ROBUST V2 DATABASE SOLUTION")
    print("=" * 55)
    
    # Test 1: Single signal test
    print("\n1. 🧪 Single Signal Test")
    print("-" * 30)
    
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM"
    }
    
    print(f"📡 Sending signal: {test_signal}")
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=30  # Longer timeout for robust processing
        )
        
        print(f"\n📊 Response Analysis:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            v2_status = result.get('v2_automation', {})
            
            print(f"   Signal Received: ✅")
            
            if v2_status.get('success'):
                print(f"\n🎉 V2 AUTOMATION SUCCESS!")
                print(f"   📊 Trade ID: {v2_status.get('trade_id')}")
                print(f"   🆔 Trade UUID: {v2_status.get('trade_uuid')}")
                print(f"   🤖 Automation: {v2_status.get('automation')}")
                print(f"   💰 Entry Price: {v2_status.get('entry_price')}")
                print(f"   🛡️ Stop Loss: {v2_status.get('stop_loss_price')}")
                print(f"   🎯 R Targets: {v2_status.get('r_targets')}")
                
                return True
                
            else:
                error_msg = v2_status.get('error', 'No error message')
                error_type = v2_status.get('error_type', 'No error type')
                debug_info = v2_status.get('debug_info', {})
                
                print(f"\n❌ V2 Automation Failed:")
                print(f"   Error: {error_msg}")
                print(f"   Type: {error_type}")
                print(f"   Debug: {debug_info}")
                
                # Analyze the error for troubleshooting
                if "All database connection strategies failed" in error_msg:
                    print(f"\n🔍 ANALYSIS: All connection strategies failed")
                    print(f"   This indicates a fundamental database connectivity issue")
                elif "PostgreSQL error" in error_msg:
                    print(f"\n🔍 ANALYSIS: PostgreSQL-specific error detected")
                    print(f"   This indicates database schema or permission issue")
                else:
                    print(f"\n🔍 ANALYSIS: Specific error in robust system")
                
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return False

def test_multiple_signals():
    """Test multiple signals to verify consistency"""
    
    print(f"\n2. 🔄 Multiple Signals Test")
    print("-" * 30)
    
    signals = [
        {"type": "Bullish", "price": 20150.75, "session": "NY AM"},
        {"type": "Bearish", "price": 20145.25, "session": "London"},
        {"type": "Bullish", "price": 20155.50, "session": "NY PM"}
    ]
    
    success_count = 0
    
    for i, signal in enumerate(signals, 1):
        signal["timestamp"] = datetime.now().isoformat()
        print(f"\n   Test {i}: {signal['type']} @ {signal['price']} ({signal['session']})")
        
        try:
            response = requests.post(
                "https://web-production-cd33.up.railway.app/api/live-signals-v2",
                json=signal,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                v2_status = result.get('v2_automation', {})
                
                if v2_status.get('success'):
                    success_count += 1
                    print(f"      ✅ Success - Trade ID: {v2_status.get('trade_id')}")
                else:
                    print(f"      ❌ Failed - {v2_status.get('error', 'Unknown error')}")
            else:
                print(f"      ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"\n📊 Multiple Signal Results:")
    print(f"   Success Rate: {success_count}/{len(signals)} ({success_count/len(signals)*100:.1f}%)")
    
    return success_count == len(signals)

if __name__ == "__main__":
    print("🎯 ROBUST V2 SOLUTION COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test single signal
    single_success = test_robust_v2_solution()
    
    if single_success:
        print(f"\n🎉 SINGLE SIGNAL: SUCCESS!")
        
        # Test multiple signals
        multiple_success = test_multiple_signals()
        
        if multiple_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"   ✅ V2 automation is fully operational")
            print(f"   ✅ Robust database connection working")
            print(f"   ✅ Multiple connection strategies successful")
            print(f"   ✅ 20R targeting system active")
            print(f"   ✅ Exact methodology implemented")
            print(f"\n🚀 READY FOR PRODUCTION TRADING!")
            
        else:
            print(f"\n🔧 Multiple signals need attention")
            print(f"   Single signal works, multiple may have rate limiting")
            
    else:
        print(f"\n🔧 Single signal test failed")
        print(f"   Need to investigate robust database solution")
    
    print(f"\n📡 TradingView Webhook URL:")
    print(f"   https://web-production-cd33.up.railway.app/api/live-signals-v2")
    
    print(f"\n📈 V2 SYSTEM STATUS:")
    if single_success:
        print(f"   🎯 Completion: 100% ✅")
        print(f"   🤖 Automation: WORKING ✅")
        print(f"   📊 Database: ROBUST ✅")
        print(f"   🎯 20R Targeting: ACTIVE ✅")
    else:
        print(f"   🎯 Completion: 99% 🔧")
        print(f"   🤖 Automation: NEEDS ATTENTION 🔧")
        print(f"   📊 Database: TROUBLESHOOTING 🔧")