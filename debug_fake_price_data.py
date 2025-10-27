#!/usr/bin/env python3

import requests
import json

def debug_fake_price_data():
    """Debug where the fake price data is coming from"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🚨 DEBUGGING FAKE PRICE DATA")
    print("=" * 50)
    
    # Test both price endpoints the dashboard uses
    endpoints = [
        "/api/v2/price/current",
        "/api/v2/price/stream?limit=1"
    ]
    
    for endpoint in endpoints:
        print(f"📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   🚨 RETURNING 200 - POTENTIAL FAKE DATA:")
                print(f"   Response: {json.dumps(data, indent=4)}")
                
                # Check for fake data patterns
                if "price" in data:
                    price = data.get("price")
                    if price == 20000.0:
                        print("   🚨 FOUND FAKE PRICE: 20000.0")
                    elif price and isinstance(price, (int, float)):
                        print(f"   🔍 Price value: {price}")
                        
                if "session" in data and data.get("session") == "London":
                    print("   🚨 FOUND FAKE SESSION: London")
                    
                if "timestamp" in data:
                    timestamp = data.get("timestamp")
                    if "05:59" in str(timestamp) or "5:59" in str(timestamp):
                        print("   🚨 FOUND FAKE TIMESTAMP: 5:59")
                        
            elif response.status_code == 404:
                print("   ✅ CORRECT 404 - No fake data")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=4)}")
            else:
                print(f"   ❌ Unexpected status: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Also check if there's cached data or other sources
    print("🔍 Checking other potential data sources...")
    
    # Check if there's any live_signals data
    try:
        response = requests.get(f"{base_url}/api/webhook-stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("   Webhook stats available - checking for price data...")
            if "price" in str(data).lower():
                print("   🔍 Found price references in webhook stats")
        else:
            print("   No webhook stats available")
    except:
        print("   Webhook stats not accessible")
    
    print()
    print("=" * 50)
    print("🎯 FAKE DATA ANALYSIS")
    print("=" * 50)
    
    print("If you're seeing:")
    print("- Price: 20000")
    print("- Session: London") 
    print("- Time: 5:59")
    print()
    print("This data is coming from:")
    print("1. A 200 response with fake data (should be 404)")
    print("2. Cached data in the browser")
    print("3. Default values in the dashboard JavaScript")
    print("4. Another endpoint returning fake data")

if __name__ == "__main__":
    debug_fake_price_data()