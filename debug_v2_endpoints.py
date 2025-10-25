#!/usr/bin/env python3
"""
Debug V2 Endpoints - Find out what's causing the errors
"""

import requests
import json

def debug_v2_endpoints():
    """Debug V2 endpoint issues"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🔧 DEBUGGING V2 ENDPOINTS")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Test 1: Simple V2 stats endpoint
    print("\n📊 Test 1: V2 Stats endpoint...")
    
    try:
        response = session.get(f"{base_url}/api/v2/stats", timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ V2 Stats working!")
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"❌ JSON parse error: {response.text[:200]}")
        else:
            print(f"❌ V2 Stats failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ V2 Stats request failed: {e}")
    
    # Test 2: Simple process signal with minimal data
    print("\n🎯 Test 2: V2 Process Signal (minimal)...")
    
    minimal_signal = {
        "type": "Bullish",
        "price": 20000
    }
    
    try:
        response = session.post(
            f"{base_url}/api/v2/process-signal",
            json=minimal_signal,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ V2 Process Signal working!")
                print(f"Trade ID: {data.get('trade_id')}")
                print(f"Entry Price: {data.get('entry_price')}")
            except:
                print(f"❌ JSON parse error: {response.text[:200]}")
        else:
            print(f"❌ V2 Process Signal failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ V2 Process Signal request failed: {e}")
    
    # Test 3: Check if endpoints exist by testing different HTTP methods
    print("\n🔍 Test 3: Endpoint existence check...")
    
    endpoints_to_test = [
        "/api/v2/stats",
        "/api/v2/active-trades", 
        "/api/v2/process-signal"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            # Test GET
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            print(f"GET {endpoint}: {response.status_code}")
            
            # Test POST
            response = session.post(f"{base_url}{endpoint}", json={}, timeout=10)
            print(f"POST {endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"❌ {endpoint} test failed: {e}")
    
    # Test 4: Test the webhook endpoint that was working
    print("\n📡 Test 4: V2 Webhook (working endpoint)...")
    
    webhook_data = {
        "type": "Bullish",
        "price": 20000,
        "session": "TEST"
    }
    
    try:
        # Test without session (no login)
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=webhook_data,
            timeout=30
        )
        
        print(f"Webhook Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ V2 Webhook endpoint accessible!")
                print(f"Message: {data.get('message', 'No message')}")
                
                v2_auto = data.get('v2_automation', {})
                print(f"V2 Automation Success: {v2_auto.get('success', False)}")
                if not v2_auto.get('success'):
                    print(f"V2 Error: {v2_auto.get('error', 'Unknown')}")
                
            except Exception as parse_error:
                print(f"❌ Webhook JSON parse error: {parse_error}")
                print(f"Raw response: {response.text[:200]}")
        else:
            print(f"❌ Webhook failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Webhook request failed: {e}")

if __name__ == "__main__":
    debug_v2_endpoints()