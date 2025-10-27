#!/usr/bin/env python3

import requests
import json

def diagnose_browser_vs_api():
    """Diagnose why browser gets different responses than direct API calls"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Diagnosing Browser vs API Response Differences")
    print("=" * 70)
    
    # Test with different headers to simulate browser vs API calls
    test_cases = [
        {
            'name': 'Direct API Call (Python)',
            'headers': {}
        },
        {
            'name': 'Browser-like Request',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'{base_url}/signal-lab-v2',
                'Origin': base_url
            }
        },
        {
            'name': 'Browser with Cookies',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'{base_url}/signal-lab-v2',
                'Origin': base_url,
                'Cookie': 'session=test'
            }
        }
    ]
    
    endpoints = [
        '/api/v2/stats',
        '/api/v2/price/current',
        '/api/v2/active-trades'
    ]
    
    for endpoint in endpoints:
        print(f"\n🎯 Testing {endpoint}")
        print("-" * 50)
        
        for test_case in test_cases:
            try:
                response = requests.get(
                    f'{base_url}{endpoint}',
                    headers=test_case['headers'],
                    timeout=10
                )
                
                status_emoji = "✅" if response.status_code == 200 else "❌"
                print(f"{status_emoji} {test_case['name']}: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"   Error: {response.text[:100]}")
                else:
                    try:
                        data = response.json()
                        if endpoint == '/api/v2/stats':
                            total = data.get('total_signals', 'N/A')
                            error = data.get('error', 'None')
                            print(f"   Total signals: {total}, Error: {error}")
                        elif endpoint == '/api/v2/active-trades':
                            trades = data.get('trades', [])
                            print(f"   Trades found: {len(trades)}")
                        elif endpoint == '/api/v2/price/current':
                            price = data.get('price', 'N/A')
                            print(f"   Price: {price}")
                    except:
                        print(f"   Response: {response.text[:100]}")
                        
            except Exception as e:
                print(f"❌ {test_case['name']}: ERROR - {e}")
    
    # Test if the issue is with the specific route
    print(f"\n🔍 Testing Route Existence")
    print("-" * 50)
    
    # Test a known working endpoint
    try:
        response = requests.get(f'{base_url}/api/webhook-health', timeout=10)
        print(f"✅ Known working endpoint (/api/webhook-health): {response.status_code}")
    except Exception as e:
        print(f"❌ Known working endpoint failed: {e}")
    
    # Test if V2 routes are even registered
    try:
        response = requests.get(f'{base_url}/api/v2/nonexistent', timeout=10)
        print(f"📍 Non-existent V2 route: {response.status_code}")
        if response.status_code == 404:
            print("   Good - V2 routes are registered (404 for non-existent)")
        elif response.status_code == 500:
            print("   Issue - V2 routes may have problems")
    except Exception as e:
        print(f"❌ Route test failed: {e}")
    
    print(f"\n📊 Analysis:")
    print("If all test cases return 200: Browser cache issue")
    print("If browser-like requests fail: CORS/Authentication issue") 
    print("If all requests fail: Deployment/Route registration issue")
    print("If non-existent route returns 500: V2 route handler broken")

if __name__ == '__main__':
    diagnose_browser_vs_api()