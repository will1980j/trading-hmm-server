#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_exact_fvg_payload():
    """Test the exact payload format being sent by the Enhanced FVG Indicator"""
    
    print("🔍 TESTING EXACT FVG PAYLOAD FORMAT")
    print("=" * 50)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Test the EXACT payload format from the Enhanced FVG Indicator
    exact_payload = {
        "signal_type": "Bullish",
        "price": 25800.50,
        "timestamp": int(datetime.now().timestamp() * 1000),
        "session": "NY_AM"
    }
    
    print("1. Testing /api/live-signals-v2 with EXACT FVG payload:")
    print(f"   Payload: {json.dumps(exact_payload, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/live-signals-v2", 
                               json=exact_payload, 
                               timeout=15)
        
        print(f"\n   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: Payload accepted")
            try:
                response_data = response.json()
                print(f"   Response JSON: {json.dumps(response_data, indent=2)}")
            except:
                print("   Response is not JSON")
        elif response.status_code == 404:
            print("   ❌ ENDPOINT NOT FOUND")
        elif response.status_code == 500:
            print("   ❌ SERVER ERROR")
        else:
            print(f"   ❌ UNEXPECTED STATUS: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ TIMEOUT: Request took too long")
    except requests.exceptions.ConnectionError:
        print("   ❌ CONNECTION ERROR: Cannot reach server")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test with different signal type
    print("\n2. Testing with Bearish signal:")
    bearish_payload = exact_payload.copy()
    bearish_payload["signal_type"] = "Bearish"
    
    try:
        response = requests.post(f"{base_url}/api/live-signals-v2", 
                               json=bearish_payload, 
                               timeout=15)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Bearish signal works")
        else:
            print("   ❌ Bearish signal failed")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test the working price streamer endpoint for comparison
    print("\n3. Testing working price streamer endpoint:")
    price_payload = {
        "type": "realtime_price",
        "symbol": "NQ",
        "price": 25800.50,
        "timestamp": int(datetime.now().timestamp() * 1000),
        "session": "NY_AM",
        "change": 0.25,
        "bid": 25800.25,
        "ask": 25800.75,
        "volume": 1000
    }
    
    try:
        response = requests.post(f"{base_url}/api/realtime-price", 
                               json=price_payload, 
                               timeout=15)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Price streamer endpoint works (for comparison)")
        else:
            print("   ❌ Price streamer endpoint failed")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n🎯 DIAGNOSIS:")
    print("If /api/live-signals-v2 returns 404:")
    print("   → Endpoint doesn't exist or wrong URL")
    print("If /api/live-signals-v2 returns 500:")
    print("   → Server error processing the payload")
    print("If /api/live-signals-v2 returns 200:")
    print("   → Payload works, issue might be with TradingView alert format")

if __name__ == "__main__":
    test_exact_fvg_payload()