#!/usr/bin/env python3
"""
🔍 SIMPLE DEPLOYMENT TEST
Test with very basic SQL to isolate the issue
"""

import requests
import json

def test_simple_sql():
    """Test with the simplest possible SQL"""
    
    print("🔍 TESTING SIMPLE SQL DEPLOYMENT")
    print("=" * 40)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Test with just a comment - should not fail
    simple_schema = "-- This is just a comment"
    
    test_data = {
        "schema_sql": simple_schema
    }
    
    print(f"\n📡 Testing with: '{simple_schema}'")
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=test_data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
            return True
        else:
            try:
                error = response.json()
                print(f"❌ Error: {error}")
            except:
                print(f"❌ Non-JSON Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_table_check():
    """Test if we can at least check existing tables"""
    
    print("\n🔍 TESTING TABLE CHECK")
    print("-" * 30)
    
    # Test with a simple SELECT to see if DB connection works
    check_schema = "SELECT COUNT(*) FROM signal_lab_trades"
    
    test_data = {
        "schema_sql": check_schema
    }
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=test_data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DB Connection works: {result}")
        else:
            error = response.json()
            print(f"❌ DB Connection issue: {error}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Test 1: Simple comment
    if test_simple_sql():
        print("✅ Basic endpoint works")
    else:
        print("❌ Basic endpoint has issues")
    
    # Test 2: Database connection
    test_table_check()