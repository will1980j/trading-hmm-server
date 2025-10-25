#!/usr/bin/env python3

import requests
import json

def test_database_connection():
    """Test database connection via a simple API call"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Test existing endpoints that should work
    endpoints_to_test = [
        "/api/webhook-health",
        "/api/webhook-stats", 
        "/api/signal-gap-check"
    ]
    
    print("🔍 TESTING DATABASE CONNECTION")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"✅ Success: {response.text[:200]}...")
            else:
                print(f"❌ Failed: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    # Test a simple database query via live signals endpoint
    print(f"\n📡 Testing live signals data...")
    try:
        response = requests.get(f"{base_url}/api/live-signals-data", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Live signals working: {len(data.get('signals', []))} signals")
        else:
            print(f"❌ Live signals failed: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Live signals request failed: {e}")

if __name__ == "__main__":
    test_database_connection()