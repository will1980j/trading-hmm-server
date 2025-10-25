#!/usr/bin/env python3

import requests

def test_authenticated_endpoints():
    """Test authenticated endpoints to verify auth is working"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🔐 TESTING AUTHENTICATION")
    print("=" * 50)
    
    # Login
    print("🔐 Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'n2351447'
    }
    
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Test authenticated endpoints
    test_endpoints = [
        "/api/webhook-health",
        "/api/webhook-stats",
        "/api/signal-gap-check"
    ]
    
    for endpoint in test_endpoints:
        print(f"\n📡 Testing {endpoint}...")
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON response: {str(data)[:100]}...")
                except:
                    print(f"✅ Text response: {response.text[:100]}...")
            else:
                print(f"❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    # Test the deployment endpoint specifically
    print(f"\n📡 Testing deployment endpoint...")
    try:
        test_payload = {"schema_sql": "-- Test"}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=test_payload,
            timeout=30
        )
        print(f"Deployment endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Deployment response: {data}")
            except:
                print(f"✅ Deployment text: {response.text}")
        else:
            print(f"❌ Deployment failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Deployment request failed: {e}")

if __name__ == "__main__":
    test_authenticated_endpoints()