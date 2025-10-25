#!/usr/bin/env python3
"""
Test V2 Webhook Direct - Test the core V2 automation
"""

import requests
import json

def test_v2_webhook_direct():
    """Test V2 webhook automation directly"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🚀 TESTING V2 WEBHOOK AUTOMATION")
    print("=" * 50)
    
    # Test 1: Bullish signal
    print("📈 Test 1: Bullish Signal Automation...")
    
    bullish_signal = {
        "type": "Bullish",
        "symbol": "NQ1!",
        "price": 20000.00,
        "timestamp": "2025-10-25T15:30:00Z",
        "session": "NY PM"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=bullish_signal,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bullish signal processed!")
            
            v2_auto = result.get('v2_automation', {})
            if v2_auto.get('success'):
                print(f"🎉 V2 AUTOMATION SUCCESS!")
                print(f"   🆔 Trade ID: {v2_auto.get('trade_id')}")
                print(f"   💰 Entry Price: ${v2_auto.get('entry_price')}")
                print(f"   🛑 Stop Loss: ${v2_auto.get('stop_loss_price')}")
                
                r_targets = v2_auto.get('r_targets', {})
                print(f"   🎯 R-Targets:")
                print(f"      1R: ${r_targets.get('1R')}")
                print(f"      5R: ${r_targets.get('5R')}")
                print(f"      10R: ${r_targets.get('10R')}")
                print(f"      20R: ${r_targets.get('20R')} 🚀")
            else:
                print(f"❌ V2 automation failed: {v2_auto.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Request exception: {e}")
    
    # Test 2: Bearish signal
    print("\n📉 Test 2: Bearish Signal Automation...")
    
    bearish_signal = {
        "type": "Bearish",
        "symbol": "NQ1!",
        "price": 20050.00,
        "timestamp": "2025-10-25T15:35:00Z",
        "session": "NY PM"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=bearish_signal,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bearish signal processed!")
            
            v2_auto = result.get('v2_automation', {})
            if v2_auto.get('success'):
                print(f"🎉 V2 AUTOMATION SUCCESS!")
                print(f"   🆔 Trade ID: {v2_auto.get('trade_id')}")
                print(f"   💰 Entry Price: ${v2_auto.get('entry_price')}")
                print(f"   🛑 Stop Loss: ${v2_auto.get('stop_loss_price')}")
                
                r_targets = v2_auto.get('r_targets', {})
                print(f"   🎯 R-Targets:")
                print(f"      1R: ${r_targets.get('1R')}")
                print(f"      5R: ${r_targets.get('5R')}")
                print(f"      10R: ${r_targets.get('10R')}")
                print(f"      20R: ${r_targets.get('20R')} 🚀")
            else:
                print(f"❌ V2 automation failed: {v2_auto.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Request exception: {e}")
    
    print("\n🎯 V2 WEBHOOK AUTOMATION TEST COMPLETE!")

if __name__ == "__main__":
    test_v2_webhook_direct()