#!/usr/bin/env python3

import requests
import json

def test_authenticated_session():
    """Test V2 endpoints with authenticated session like a real browser"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Testing V2 Endpoints with Authenticated Session")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Try to access the V2 dashboard page (should redirect to login)
    print("1. Testing V2 dashboard page access...")
    try:
        response = session.get(f'{base_url}/signal-lab-v2', timeout=10)
        print(f"   V2 Dashboard: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Redirected to login (expected)")
        elif response.status_code == 200:
            print("   ✅ Dashboard accessible (already logged in)")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 2: Test V2 API endpoints without authentication
    print("\n2. Testing V2 API endpoints (should be public)...")
    
    endpoints = [
        ('/api/v2/stats', 'V2 Stats'),
        ('/api/v2/active-trades', 'V2 Active Trades'),
        ('/api/v2/price/current', 'V2 Price Current')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = session.get(f'{base_url}{endpoint}', timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: Working (200)")
                
                # Show some data
                try:
                    data = response.json()
                    if 'stats' in endpoint:
                        total = data.get('total_signals', 0)
                        error = data.get('error', 'None')
                        print(f"      Total signals: {total}, Error: {error}")
                    elif 'active-trades' in endpoint:
                        trades = data.get('trades', [])
                        print(f"      Trades found: {len(trades)}")
                    elif 'price' in endpoint:
                        price = data.get('price', 'N/A')
                        print(f"      Price: {price}")
                except:
                    print(f"      Response: {response.text[:50]}...")
                    
            else:
                print(f"   ❌ {name}: Failed ({response.status_code})")
                print(f"      Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
    
    # Step 3: Test with browser-like headers
    print("\n3. Testing with browser-like headers...")
    
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f'{base_url}/signal-lab-v2',
        'Origin': base_url,
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = session.get(
            f'{base_url}/api/v2/stats',
            headers=browser_headers,
            timeout=10
        )
        print(f"   Browser-like request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_signals', 0)
            print(f"   ✅ Working with browser headers - Total: {total}")
        else:
            print(f"   ❌ Failed with browser headers: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Browser headers test failed: {e}")
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS:")
    print("If all endpoints return 200: The issue is browser cache")
    print("If endpoints fail: There's a server-side authentication issue")
    print("If browser headers fail: There's a CORS or session issue")

if __name__ == '__main__':
    test_authenticated_session()