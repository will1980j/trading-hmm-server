#!/usr/bin/env python3

import requests
import json

def debug_v2_stats():
    """Debug the V2 stats endpoint error"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Debugging V2 Stats Endpoint Error")
    print("=" * 50)
    
    try:
        response = requests.get(f'{base_url}/api/v2/stats', timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("\n❌ 500 Internal Server Error Details:")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw Error Response: {response.text}")
        elif response.status_code == 200:
            print("\n✅ Success Response:")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"\n⚠️ Unexpected Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Also test other V2 endpoints
    print("\n" + "=" * 50)
    print("Testing Other V2 Endpoints:")
    
    endpoints = [
        '/api/v2/active-trades',
        '/api/v2/price/current'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f"\n{endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:200]}")
        except Exception as e:
            print(f"\n{endpoint}: ERROR - {e}")

if __name__ == '__main__':
    debug_v2_stats()