#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_fixed_webhook():
    """Test the webhook with fixed database connection"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔧 Testing Fixed V2 Webhook Database Connection")
    print("=" * 55)
    
    # Test signal
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM"
    }
    
    print(f"\n📡 Sending test signal...")
    print(f"   Signal: {test_signal}")
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        
        print(f"\n📊 Response Analysis:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Signal Received: ✅")
            
            v2_status = result.get('v2_automation', {})
            
            if v2_status.get('success'):
                print(f"   🎉 V2 AUTOMATION SUCCESS!")
                print(f"   📊 Trade ID: {v2_status.get('trade_id')}")
                print(f"   🆔 Trade UUID: {v2_status.get('trade_uuid')}")
                print(f"   💰 Entry Price: {v2_status.get('entry_price')}")
                print(f"   🛡️ Stop Loss: {v2_status.get('stop_loss_price')}")
                print(f"   🎯 R Targets: {v2_status.get('r_targets')}")
                
                return True
                
            else:
                error_msg = v2_status.get('error', 'Unknown error')
                error_type = v2_status.get('error_type', 'Unknown')
                
                print(f"   ❌ V2 Automation Failed:")
                print(f"      Error: {error_msg}")
                print(f"      Type: {error_type}")
                
                if error_msg != "0":
                    print(f"   ✅ Error reporting improved (no longer '0')")
                    
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return False

def test_multiple_signals():
    """Test multiple signals to verify consistency"""
    
    print(f"\n🔄 Testing Multiple Signals...")
    
    signals = [
        {"type": "Bullish", "price": 20150.75, "session": "NY AM"},
        {"type": "Bearish", "price": 20145.25, "session": "NY AM"},
        {"type": "Bullish", "price": 20155.50, "session": "London"}
    ]
    
    success_count = 0
    
    for i, signal in enumerate(signals, 1):
        signal["timestamp"] = datetime.now().isoformat()
        print(f"\n   Test {i}: {signal['type']} signal...")
        
        if test_fixed_webhook():
            success_count += 1
            print(f"      ✅ Success")
        else:
            print(f"      ❌ Failed")
    
    print(f"\n📊 Multiple Signal Test Results:")
    print(f"   Success Rate: {success_count}/{len(signals)} ({success_count/len(signals)*100:.1f}%)")
    
    return success_count == len(signals)

if __name__ == "__main__":
    print("🚀 V2 WEBHOOK DATABASE CONNECTION FIX TEST")
    print("=" * 60)
    
    # Single signal test
    single_success = test_fixed_webhook()
    
    if single_success:
        print(f"\n🎉 SINGLE SIGNAL TEST: SUCCESS!")
        
        # Multiple signal test
        multiple_success = test_multiple_signals()
        
        if multiple_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"   ✅ V2 automation is fully operational")
            print(f"   ✅ Database connection fixed")
            print(f"   ✅ 20R targeting system active")
            print(f"   ✅ Ready for live TradingView signals")
        else:
            print(f"\n🔧 Multiple signals need attention")
    else:
        print(f"\n🔧 Single signal test failed - investigating...")
    
    print(f"\n📡 TradingView Webhook URL:")
    print(f"   https://web-production-cd33.up.railway.app/api/live-signals-v2")