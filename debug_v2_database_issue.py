#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def debug_v2_issue():
    """Debug the V2 database issue"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 Debugging V2 Database Issue")
    print("=" * 50)
    
    # Test 1: Check if V2 table exists
    print("\n1. Testing V2 Stats (should show table info)...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            # Try to get JSON response
            try:
                data = response.json()
                print(f"   ✅ V2 Stats JSON: {json.dumps(data, indent=2)}")
            except:
                # If not JSON, it might be HTML (login page)
                text = response.text
                if "login" in text.lower() or "<!doctype" in text.lower():
                    print("   ❌ Getting login page instead of API response")
                    print("   🔧 This suggests authentication issue with V2 endpoints")
                else:
                    print(f"   📄 Response text: {text[:200]}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Test webhook with detailed error capture
    print("\n2. Testing webhook with error capture...")
    
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM",
        "debug": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   📊 Full webhook response:")
            print(json.dumps(result, indent=4))
            
            # Analyze the error
            v2_status = result.get('v2_automation', {})
            error_msg = v2_status.get('error', 'No error field')
            
            if error_msg == "0":
                print("   🔍 Error '0' suggests database constraint or SQL error")
                print("   💡 Possible causes:")
                print("      - Missing required fields in database insert")
                print("      - Database constraint violations")
                print("      - PostgreSQL function errors")
            
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 3: Check if we can access V2 active trades
    print("\n3. Testing V2 active trades endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v2/active-trades", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Active trades JSON: {json.dumps(data, indent=2)}")
            except:
                text = response.text
                if "login" in text.lower():
                    print("   ❌ Getting login page - authentication issue")
                else:
                    print(f"   📄 Response: {text[:200]}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("   The V2 system is receiving signals but failing during database operations")
    print("   This suggests either:")
    print("   1. Database table/function missing")
    print("   2. Authentication issue with V2 endpoints") 
    print("   3. SQL constraint violation in insert")
    print("\n🔧 NEXT STEPS:")
    print("   1. Verify V2 database schema is deployed")
    print("   2. Check if V2 endpoints require authentication")
    print("   3. Test database connection directly")

if __name__ == "__main__":
    debug_v2_issue()