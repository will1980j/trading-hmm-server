#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_fvg_webhook_endpoint():
    """Test the /api/live-signals-v2 endpoint with FVG indicator data"""
    
    print("🔍 TESTING FVG WEBHOOK ENDPOINT")
    print("=" * 50)
    
    base_url = "https://web-production-cd33.up.railway.app"
    endpoint = "/api/live-signals-v2"
    
    # Create test payload matching Enhanced FVG Indicator format
    test_payload = {
        "signal_type": "Bullish",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "session": "NY_AM",
        "signal_candle": {
            "open": 25800.50,
            "high": 25825.75,
            "low": 25795.25,
            "close": 25820.00,
            "volume": 1500
        },
        "previous_candle": {
            "open": 25790.00,
            "high": 25810.50,
            "low": 25785.00,
            "close": 25805.25
        },
        "market_context": {
            "atr": 45.75,
            "volatility": 32.50,
            "signal_strength": 85.0
        },
        "fvg_data": {
            "bias": "Bullish",
            "htf_status": "1H:Bullish 15M:Bullish 5M:Bullish",
            "signal_type": "FVG",
            "htf_aligned": True,
            "engulfing": {
                "bullish": False,
                "bearish": False,
                "sweep_bullish": False,
                "sweep_bearish": False
            }
        },
        "methodology_data": {
            "requires_confirmation": True,
            "stop_loss_buffer": 25
        }
    }
    
    print("1. Testing /api/live-signals-v2 endpoint:")
    print(f"   URL: {base_url}{endpoint}")
    print(f"   Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}{endpoint}", 
                               json=test_payload, 
                               timeout=10)
        
        print(f"\n2. Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("   ✅ SUCCESS: Webhook accepted")
                print(f"   Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print("   ✅ SUCCESS: Webhook accepted (non-JSON response)")
        elif response.status_code == 404:
            print("   ❌ ENDPOINT NOT FOUND: /api/live-signals-v2 doesn't exist")
        elif response.status_code == 500:
            print("   ❌ SERVER ERROR: Endpoint exists but has processing error")
        else:
            print(f"   ❌ UNEXPECTED STATUS: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ TIMEOUT: Request took too long")
    except requests.exceptions.ConnectionError:
        print("   ❌ CONNECTION ERROR: Cannot reach server")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test the original endpoint for comparison
    print("\n3. Testing original /api/live-signals endpoint:")
    
    # Simplified payload for original endpoint
    simple_payload = {
        "signal_type": "Bullish",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "session": "NY_AM",
        "price": 25820.00
    }
    
    try:
        response = requests.post(f"{base_url}/api/live-signals", 
                               json=simple_payload, 
                               timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Original endpoint working")
        else:
            print("   ❌ Original endpoint has issues")
            
    except Exception as e:
        print(f"   ❌ Original endpoint error: {str(e)}")
    
    print("\n4. DIAGNOSIS:")
    print("If /api/live-signals-v2 returns 404:")
    print("   → Endpoint not deployed to Railway")
    print("If /api/live-signals-v2 returns 500:")
    print("   → Endpoint exists but has processing errors")
    print("If /api/live-signals-v2 returns 200:")
    print("   → Endpoint working, issue might be with TradingView alert setup")

if __name__ == "__main__":
    test_fvg_webhook_endpoint()