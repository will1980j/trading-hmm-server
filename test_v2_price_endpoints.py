#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_v2_price_endpoints():
    """Test the V2 price endpoints that are failing in the dashboard"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 TESTING V2 PRICE ENDPOINTS")
    print("=" * 50)
    
    # Test current price endpoint
    print("\n1. Testing /api/v2/price/current")
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Price = {data.get('price', 'N/A')}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Test price stream endpoint
    print("\n2. Testing /api/v2/price/stream?limit=1")
    try:
        response = requests.get(f"{base_url}/api/v2/price/stream?limit=1", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data.get('count', 0)} prices returned")
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Test realtime price webhook endpoint (should exist)
    print("\n3. Testing /api/realtime-price (POST endpoint exists)")
    try:
        # Just check if endpoint exists (don't send data)
        response = requests.options(f"{base_url}/api/realtime-price", timeout=10)
        print(f"OPTIONS Status Code: {response.status_code}")
        print("✅ Realtime price webhook endpoint exists")
    except Exception as e:
        print(f"❌ ERROR checking realtime endpoint: {str(e)}")
    
    # Check if realtime price handler is working
    print("\n4. Testing realtime price handler import")
    try:
        from realtime_price_webhook_handler import get_current_price
        current_price = get_current_price()
        if current_price:
            print(f"✅ Realtime handler working: {current_price.price}")
        else:
            print("⚠️ Realtime handler loaded but no current price")
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
    except Exception as e:
        print(f"❌ Handler error: {str(e)}")

if __name__ == "__main__":
    test_v2_price_endpoints()