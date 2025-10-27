#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def check_realtime_price_status():
    """Check the status of realtime price data"""
    
    print("🔍 CHECKING REALTIME PRICE DATA STATUS")
    print("=" * 50)
    
    # Check if we have any realtime price data in the system
    try:
        from realtime_price_webhook_handler import get_current_price, get_recent_prices
        
        print("\n1. Current Price Status:")
        current = get_current_price()
        if current:
            print(f"✅ Current Price: {current.price}")
            print(f"   Timestamp: {datetime.fromtimestamp(current.timestamp/1000)}")
            print(f"   Session: {current.session}")
            print(f"   Change: {current.change}")
        else:
            print("❌ No current price available")
        
        print("\n2. Recent Prices Status:")
        recent = get_recent_prices(limit=5)
        if recent:
            print(f"✅ Found {len(recent)} recent prices:")
            for i, price in enumerate(recent[:3]):
                print(f"   {i+1}. {price.price} at {datetime.fromtimestamp(price.timestamp/1000)}")
        else:
            print("❌ No recent prices available")
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test sending a sample price update
    print("\n3. Testing Price Update:")
    try:
        base_url = "https://web-production-cd33.up.railway.app"
        
        # Send a test price update
        test_data = {
            "price": 20000.50,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "session": "NY AM",
            "change": 0.25,
            "bid": 20000.25,
            "ask": 20000.75,
            "volume": 1000
        }
        
        response = requests.post(f"{base_url}/api/realtime-price", 
                               json=test_data, 
                               timeout=10)
        
        print(f"Test update status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Test price update successful")
            
            # Now test the V2 endpoints again
            print("\n4. Re-testing V2 endpoints after update:")
            
            current_response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
            print(f"Current price endpoint: {current_response.status_code}")
            if current_response.status_code == 200:
                data = current_response.json()
                print(f"✅ Current price now available: {data.get('price')}")
            
        else:
            print(f"❌ Test update failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test update error: {str(e)}")

if __name__ == "__main__":
    check_realtime_price_status()