#!/usr/bin/env python3

import requests
import json

def fix_v2_stats_final():
    """Final fix for V2 stats endpoint"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔧 FINAL V2 STATS FIX")
    print("=" * 50)
    
    # Test 1: Check if V2 table exists by trying to create a record
    print("1. Testing V2 table existence...")
    try:
        test_signal = {
            "type": "Bullish",
            "price": 25834.25,
            "timestamp": 1698765432000,
            "session": "NY AM",
            "symbol": "NQ"
        }
        
        response = requests.post(f"{base_url}/api/live-signals-v2", json=test_signal, timeout=10)
        print(f"   V2 webhook status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            v2_automation = data.get("v2_automation", {})
            
            if v2_automation.get("success"):
                print("   ✅ V2 table exists and working!")
                print(f"   Created trade ID: {v2_automation.get('trade_id')}")
            else:
                print("   ⚠️  V2 webhook responds but automation failed")
                print(f"   Reason: {v2_automation.get('reason', 'Unknown')}")
        else:
            print(f"   ❌ V2 webhook failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Try to deploy V2 schema if needed
    print("2. Attempting to deploy V2 schema...")
    try:
        response = requests.post(f"{base_url}/api/deploy-signal-lab-v2", timeout=30)
        print(f"   Schema deployment status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Schema deployment successful!")
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ⚠️  Schema deployment response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Schema deployment error: {e}")
    
    print()
    
    # Test 3: Test stats endpoint after potential fixes
    print("3. Testing V2 stats endpoint after fixes...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "Database query failed" in str(data.get("error", "")):
                print("   ❌ Still failing with database error")
                print("   This suggests the table exists but has wrong schema")
            else:
                print("   ✅ SUCCESS! Stats endpoint working!")
                print(f"   Total signals: {data.get('total_signals', 0)}")
                print(f"   Active trades: {data.get('active_trades', 0)}")
        else:
            print(f"   ❌ Stats endpoint error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Stats test error: {e}")
    
    print()
    print("=" * 50)
    print("🎯 DIAGNOSIS")
    print("=" * 50)
    
    print("If V2 webhook works but stats fails:")
    print("- The signal_lab_v2_trades table exists")
    print("- But the stats query is using wrong column names")
    print("- Need to check actual table schema vs query")
    print()
    print("If both fail:")
    print("- The signal_lab_v2_trades table doesn't exist")
    print("- Need to deploy the V2 schema")

if __name__ == "__main__":
    fix_v2_stats_final()