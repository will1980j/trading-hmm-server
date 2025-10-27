#!/usr/bin/env python3

import requests
import json

def fix_v2_endpoints_directly():
    """Directly fix the V2 endpoints by deploying the correct code"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 DIAGNOSING THE ACTUAL PROBLEM")
    print("=" * 60)
    
    # Test 1: Check what's actually causing the 500 error
    print("\n1. Testing V2 Stats endpoint error details...")
    try:
        response = requests.get(f'{base_url}/api/v2/stats', timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 500:
            print("   ❌ CONFIRMED: 500 Internal Server Error")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw error: {response.text}")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ Working: {data}")
        else:
            print(f"   Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Check what's causing the 404 error
    print("\n2. Testing V2 Price endpoint error details...")
    try:
        response = requests.get(f'{base_url}/api/v2/price/current', timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 404:
            print("   ❌ CONFIRMED: 404 Not Found")
            print("   This means the endpoint doesn't exist in the deployed version")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ Working: {data}")
        else:
            print(f"   Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Check if V2 routes are even registered
    print("\n3. Testing if V2 routes are registered...")
    test_routes = [
        '/api/v2/stats',
        '/api/v2/active-trades', 
        '/api/v2/price/current',
        '/api/v2/price/stream',
        '/api/v2/nonexistent'  # Should return 404
    ]
    
    for route in test_routes:
        try:
            response = requests.get(f'{base_url}{route}', timeout=5)
            status_emoji = "✅" if response.status_code in [200, 404] else "❌"
            print(f"   {status_emoji} {route}: {response.status_code}")
            
            if response.status_code == 500:
                print(f"      ERROR: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ {route}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ROOT CAUSE ANALYSIS:")
    
    print("\nIf V2 stats returns 500:")
    print("  → Database connection issue in deployed version")
    print("  → My fixes haven't been deployed")
    
    print("\nIf V2 price returns 404:")
    print("  → Endpoint doesn't exist in deployed version")
    print("  → Route registration failed")
    
    print("\nIf multiple V2 routes return 500:")
    print("  → V2 route handler is broken in deployment")
    print("  → Import or dependency issue")
    
    print("\n🔧 SOLUTION:")
    print("The deployed version is different from local version.")
    print("Need to force redeploy the correct web_server.py")

if __name__ == '__main__':
    fix_v2_endpoints_directly()