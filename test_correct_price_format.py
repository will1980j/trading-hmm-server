#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_correct_price_format():
    """Test the realtime price webhook with the correct format"""
    
    print("🔍 TESTING CORRECT REALTIME PRICE FORMAT")
    print("=" * 50)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Send a test price update with the correct format
    print("\n1. Sending correctly formatted price update:")
    
    test_data = {
        "type": "realtime_price",  # This is the key field that was missing!
        "symbol": "NQ",
        "price": 20000.50,
        "timestamp": int(datetime.now().timestamp() * 1000),
        "session": "NY AM",
        "change": 0.25,
        "bid": 20000.25,
        "ask": 20000.75,
        "volume": 1000
    }
    
    print(f"Sending data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/api/realtime-price", 
                               json=test_data, 
                               timeout=10)
        
        print(f"\nWebhook Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                print("✅ Price update successful!")
                
                # Now test the V2 endpoints
                print("\n2. Testing V2 endpoints after successful update:")
                
                # Test current price
                current_response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
                print(f"\nCurrent price endpoint: {current_response.status_code}")
                if current_response.status_code == 200:
                    data = current_response.json()
                    print(f"✅ Current price: {data.get('price')}")
                    print(f"   Session: {data.get('session')}")
                    print(f"   Timestamp: {data.get('timestamp')}")
                else:
                    print(f"❌ Current price failed: {current_response.text}")
                
                # Test price stream
                stream_response = requests.get(f"{base_url}/api/v2/price/stream?limit=1", timeout=10)
                print(f"\nPrice stream endpoint: {stream_response.status_code}")
                if stream_response.status_code == 200:
                    data = stream_response.json()
                    print(f"✅ Price stream: {data.get('count')} prices")
                    if data.get('prices'):
                        print(f"   Latest price: {data['prices'][0].get('price')}")
                else:
                    print(f"❌ Price stream failed: {stream_response.text}")
                    
            else:
                print(f"❌ Price update failed: {response_data}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test multiple price updates
    print("\n3. Testing multiple price updates:")
    for i in range(3):
        test_data['price'] = 20000.50 + (i * 0.25)
        test_data['timestamp'] = int(datetime.now().timestamp() * 1000)
        
        try:
            response = requests.post(f"{base_url}/api/realtime-price", 
                                   json=test_data, 
                                   timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   Update {i+1}: ✅ Price {test_data['price']} - {data.get('status')}")
            else:
                print(f"   Update {i+1}: ❌ Failed")
        except Exception as e:
            print(f"   Update {i+1}: ❌ Error: {str(e)}")

if __name__ == "__main__":
    test_correct_price_format()