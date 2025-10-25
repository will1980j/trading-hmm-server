#!/usr/bin/env python3
"""
Simple direct test of V2 endpoint
"""

import requests

def test_v2_direct():
    """Test V2 endpoint directly"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🧪 DIRECT V2 TEST")
    print("=" * 30)
    
    # Test webhook (no auth required)
    webhook_data = {
        "type": "Bullish",
        "price": 20000
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=webhook_data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook working!")
            
            v2_auto = data.get('v2_automation', {})
            print(f"V2 Success: {v2_auto.get('success')}")
            print(f"Entry Price: {v2_auto.get('entry_price')}")
            print(f"Stop Loss: {v2_auto.get('stop_loss_price')}")
            
            if v2_auto.get('entry_price') is None and v2_auto.get('stop_loss_price') is None:
                print("✅ CORRECT: No fake calculations!")
            else:
                print("❌ WRONG: Still calculating fake prices!")
                
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_v2_direct()