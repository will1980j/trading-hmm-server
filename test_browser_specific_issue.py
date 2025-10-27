#!/usr/bin/env python3

import requests

def test_browser_specific_issue():
    """Test for browser-specific issues that could cause 500/404"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 TESTING BROWSER-SPECIFIC ISSUES")
    print("=" * 60)
    
    # Test with exact browser headers
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': f'{base_url}/signal-lab-v2',
        'Origin': base_url,
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    
    print("1. Testing with exact Chrome headers...")
    try:
        response = requests.get(f'{base_url}/api/v2/stats', headers=browser_headers, timeout=10)
        print(f"   V2 Stats with Chrome headers: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ FOUND THE ISSUE: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
        else:
            data = response.json()
            print(f"   ✅ Working with Chrome headers: {data.get('total_signals', 'N/A')} signals")
            
    except Exception as e:
        print(f"   ❌ Chrome headers test failed: {e}")
    
    print("\n2. Testing CORS preflight...")
    try:
        # Test OPTIONS request (CORS preflight)
        response = requests.options(f'{base_url}/api/v2/stats', headers=browser_headers, timeout=10)
        print(f"   CORS preflight: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ CORS issue detected: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
        else:
            print(f"   ✅ CORS working")
            
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    print("\n3. Testing with session cookies...")
    session = requests.Session()
    
    # First, try to get the dashboard page to establish session
    try:
        dashboard_response = session.get(f'{base_url}/signal-lab-v2', timeout=10)
        print(f"   Dashboard page: {dashboard_response.status_code}")
        
        # Now test API with session
        api_response = session.get(f'{base_url}/api/v2/stats', headers=browser_headers, timeout=10)
        print(f"   V2 Stats with session: {api_response.status_code}")
        
        if api_response.status_code != 200:
            print(f"   ❌ Session issue: {api_response.text[:200]}")
        else:
            data = api_response.json()
            print(f"   ✅ Working with session: {data.get('total_signals', 'N/A')} signals")
            
    except Exception as e:
        print(f"   ❌ Session test failed: {e}")
    
    print("\n4. Testing direct URL access...")
    direct_urls = [
        f'{base_url}/api/v2/stats',
        f'{base_url}/api/v2/price/current'
    ]
    
    for url in direct_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"   {url}: {response.status_code}")
        except Exception as e:
            print(f"   {url}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("If ALL tests return 200: Your browser has a specific issue")
    print("If Chrome headers fail: CORS/Header issue")
    print("If session test fails: Authentication issue")
    print("If direct URLs fail: Server routing issue")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Try a completely different browser (Firefox, Edge)")
    print("2. Try on a different computer/network")
    print("3. Check if antivirus/firewall is blocking requests")

if __name__ == '__main__':
    test_browser_specific_issue()