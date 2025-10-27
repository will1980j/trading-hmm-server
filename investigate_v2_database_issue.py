#!/usr/bin/env python3

import requests
import json

def investigate_v2_database_issue():
    """Deep investigation of the V2 database issue"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 INVESTIGATING V2 DATABASE ISSUE")
    print("=" * 50)
    
    # Test 1: Check if signal_lab_v2_trades table exists
    print("1. Testing V2 webhook to see if table exists...")
    try:
        test_signal = {
            "signal": "bullish",
            "price": 20500.75,
            "timestamp": 1698765432000,
            "session": "NY AM",
            "symbol": "NQ"
        }
        
        response = requests.post(f"{base_url}/api/live-signals-v2", json=test_signal, timeout=10)
        print(f"   Webhook status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            if "trade_id" in str(data) or "Trade ID" in str(data):
                print("   ✅ Table exists - webhook can create records")
            else:
                print("   ❌ Table issue - webhook not creating records")
        else:
            print(f"   ❌ Webhook failing: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Check what the stats endpoint is actually doing
    print("2. Detailed stats endpoint investigation...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Full response: {json.dumps(data, indent=2)}")
            
            # Check for specific error patterns
            error_msg = data.get("error", "")
            if "Database query failed: 0" in str(error_msg):
                print("   🔍 FOUND THE ISSUE: 'Database query failed: 0'")
                print("   This suggests psycopg2 is returning error code 0")
                print("   Likely causes:")
                print("   - Column doesn't exist in table")
                print("   - Table exists but has different schema")
                print("   - Query syntax error")
            elif "Database not available" in str(error_msg):
                print("   🔍 Database connection issue")
            else:
                print("   🔍 Different error pattern")
                
        else:
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Check the price endpoint error
    print("3. Price endpoint investigation...")
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        elif response.status_code == 404:
            data = response.json()
            print(f"   404 Response: {json.dumps(data, indent=2)}")
            if "No real price data available" in str(data):
                print("   ✅ This is expected - no live_signals data")
        elif response.status_code == 500:
            print(f"   500 Error: {response.text[:300]}")
            print("   🔍 This suggests a code error, not missing endpoint")
        else:
            print(f"   Unexpected status: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Check if we can query the table directly
    print("4. Testing direct table access via webhook stats...")
    try:
        response = requests.get(f"{base_url}/api/webhook-stats", timeout=10)
        print(f"   Webhook stats status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ General database access works")
            # Look for V2 related data
            if "v2" in str(data).lower():
                print("   🔍 Found V2 references in webhook stats")
        else:
            print("   ❌ General database access failing")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 50)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    print("Based on the investigation above:")
    print("1. If webhook works but stats fails → Column name mismatch")
    print("2. If both fail → Table doesn't exist")
    print("3. If price endpoint 500s → Code error in endpoint")
    print("4. If price endpoint 404s → Expected (no data)")
    
    print()
    print("🔧 NEXT STEPS:")
    print("- Check the actual V2 table schema in database")
    print("- Verify column names match the queries")
    print("- Fix any schema mismatches")

if __name__ == "__main__":
    investigate_v2_database_issue()