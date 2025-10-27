#!/usr/bin/env python3

import requests
import json
import time

def test_realtime_price_integration():
    """Test the complete realtime price integration"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🚀 TESTING REALTIME PRICE INTEGRATION")
    print("=" * 50)
    
    # Step 1: Send realtime price data
    print("1. Sending realtime price data...")
    try:
        price_data = {
            "type": "realtime_price",
            "symbol": "NQ",
            "price": 20502.75,
            "timestamp": int(time.time() * 1000),
            "session": "NY AM",
            "volume": 150,
            "bid": 20502.50,
            "ask": 20503.00,
            "change": 2.75
        }
        
        response = requests.post(f"{base_url}/api/realtime-price", json=price_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Realtime price sent successfully!")
            print(f"   Price: ${data.get('price')}")
            print(f"   Session: {data.get('session')}")
        else:
            print(f"   ❌ Failed to send price: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error sending price: {e}")
        return False
    
    print()
    
    # Step 2: Wait a moment for processing
    print("2. Waiting for price processing...")
    time.sleep(2)
    
    # Step 3: Test V2 current price endpoint
    print("3. Testing V2 current price endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS! V2 price endpoint working with realtime data!")
            print(f"   Price: ${data.get('price')}")
            print(f"   Session: {data.get('session')}")
            print(f"   Change: {data.get('change')}")
            print(f"   Source: {data.get('source')}")
        elif response.status_code == 404:
            data = response.json()
            print("   ⚠️ No price data available yet")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   ❌ Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error testing current price: {e}")
    
    print()
    
    # Step 4: Test V2 price stream endpoint
    print("4. Testing V2 price stream endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v2/price/stream?limit=1", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS! V2 price stream working with realtime data!")
            print(f"   Count: {data.get('count')}")
            if data.get('prices'):
                price = data['prices'][0]
                print(f"   Price: ${price.get('price')}")
                print(f"   Session: {price.get('session')}")
                print(f"   Source: {price.get('source')}")
        elif response.status_code == 404:
            data = response.json()
            print("   ⚠️ No price stream data available yet")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   ❌ Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error testing price stream: {e}")
    
    print()
    print("=" * 50)
    print("🎯 INTEGRATION TEST COMPLETE")
    print("=" * 50)
    
    print("If both V2 endpoints return 200 with real price data:")
    print("✅ Integration successful - dashboard will show real prices")
    print()
    print("If endpoints return 404:")
    print("⚠️ Price data not persisting - may need handler restart")
    print()
    print("Next steps:")
    print("1. Configure TradingView 1-second indicator with /api/realtime-price webhook")
    print("2. Verify continuous price updates")
    print("3. Check dashboard shows real-time prices")

if __name__ == "__main__":
    test_realtime_price_integration()