#!/usr/bin/env python3
"""
🔍 TEST DEPLOYMENT ENDPOINT
Check what's causing the 500 error
"""

import requests
import json

def test_endpoint():
    """Test the deployment endpoint with minimal data"""
    
    print("🔍 TESTING DEPLOYMENT ENDPOINT")
    print("=" * 40)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Test with minimal schema first
    test_schema = """
    -- Test comment
    SELECT 1;
    """
    
    test_data = {
        "action": "test_deploy",
        "schema_sql": test_schema
    }
    
    print("\n📡 Testing with minimal schema...")
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=test_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 500:
            print("\n❌ 500 Error Response:")
            print(response.text[:500])  # First 500 chars
            
            # Try to parse as JSON
            try:
                error_data = response.json()
                print(f"\nError Details: {error_data}")
            except:
                print("Response is not JSON (likely HTML error page)")
        
        elif response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Success: {result}")
            except:
                print("✅ Success but response not JSON")
        
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(response.text[:200])
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_endpoint()