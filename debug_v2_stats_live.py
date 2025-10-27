#!/usr/bin/env python3

import requests
import json

def test_v2_stats_endpoint():
    """Test the V2 stats endpoint that's failing in browser"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 DEBUGGING V2 STATS ENDPOINT")
    print("=" * 50)
    
    # Test the failing endpoint
    try:
        print("📡 Testing /api/v2/stats endpoint...")
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ SUCCESS - Response data:")
                print(json.dumps(data, indent=2))
            except:
                print("❌ Response not JSON:")
                print(response.text[:500])
        else:
            print("❌ FAILED - Response:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    
    # Test the price endpoint too
    try:
        print("📡 Testing /api/v2/price/current endpoint...")
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ SUCCESS - Response data:")
                print(json.dumps(data, indent=2))
            except:
                print("❌ Response not JSON:")
                print(response.text[:500])
        else:
            print("❌ FAILED - Response:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_v2_stats_endpoint()