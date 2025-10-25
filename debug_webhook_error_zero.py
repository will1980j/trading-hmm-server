#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def debug_error_zero():
    """Debug the specific error '0' issue"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 Debugging Webhook Error '0'")
    print("=" * 40)
    
    # Test 1: Check if we can access any V2 endpoint without auth
    print("\n1. Testing V2 table existence via deployment endpoint...")
    
    # Simple table check SQL
    check_sql = """
    SELECT COUNT(*) FROM signal_lab_v2_trades;
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json={"schema_sql": check_sql},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Table check result: {result}")
        else:
            print(f"   ❌ Table check failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Try a simple insert via deployment endpoint
    print("\n2. Testing direct V2 insert...")
    
    insert_sql = """
    INSERT INTO signal_lab_v2_trades (
        trade_uuid, symbol, bias, session, 
        date, time, entry_price, stop_loss_price, risk_distance,
        target_1r_price, target_2r_price, target_3r_price,
        target_5r_price, target_10r_price, target_20r_price,
        current_mfe, trade_status, active_trade, auto_populated
    ) VALUES (
        gen_random_uuid(), 'NQ1!', 'Bullish', 'NY AM',
        CURRENT_DATE, CURRENT_TIME, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL,
        0.00, 'pending_confirmation', false, true
    ) RETURNING id, trade_uuid;
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json={"schema_sql": insert_sql},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Direct insert result: {result}")
        else:
            print(f"   ❌ Direct insert failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 3: Test webhook with detailed logging
    print("\n3. Testing webhook with analysis...")
    
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM"
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
            print(f"   📊 Full response: {json.dumps(result, indent=2)}")
            
            v2_status = result.get('v2_automation', {})
            error_msg = v2_status.get('error', 'No error field')
            
            print(f"\n   🔍 Error Analysis:")
            print(f"      - Error value: '{error_msg}'")
            print(f"      - Error type: {type(error_msg)}")
            
            if str(error_msg) == "0":
                print(f"      💡 This suggests:")
                print(f"         - Database connection issue")
                print(f"         - SQL constraint violation")
                print(f"         - Exception being caught but str() returns '0'")
                print(f"         - Possible integer error code being converted to string")
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 ERROR '0' ANALYSIS:")
    print("   The webhook is receiving signals correctly")
    print("   The V2 automation code is running")
    print("   But database operations are failing silently")
    print("   Error '0' suggests exception handling issue")

if __name__ == "__main__":
    debug_error_zero()