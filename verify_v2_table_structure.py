#!/usr/bin/env python3

import requests
import json

def verify_table_structure():
    """Verify the V2 table structure matches our insert"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 Verifying V2 Table Structure")
    print("=" * 40)
    
    # Check if table exists and get structure
    check_table_sql = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'signal_lab_v2_trades'
    ORDER BY ordinal_position;
    """
    
    print("\n1. Checking table structure...")
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json={"schema_sql": check_table_sql},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Table structure query successful")
            print(f"   📊 Result: {result}")
        else:
            print(f"   ❌ Table structure query failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test a simple insert to see what fails
    print("\n2. Testing simple insert...")
    
    simple_insert_sql = """
    INSERT INTO signal_lab_v2_trades (
        trade_uuid, symbol, bias, session, 
        date, time, current_mfe, trade_status, active_trade, auto_populated
    ) VALUES (
        gen_random_uuid(), 'NQ1!', 'Bullish', 'NY AM',
        CURRENT_DATE, CURRENT_TIME, 0.00, 'pending_confirmation', false, true
    ) RETURNING id, trade_uuid;
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json={"schema_sql": simple_insert_sql},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Simple insert successful")
            print(f"   📊 Result: {result}")
        else:
            print(f"   ❌ Simple insert failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test the exact insert from webhook
    print("\n3. Testing exact webhook insert...")
    
    webhook_insert_sql = """
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
            json={"schema_sql": webhook_insert_sql},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Webhook insert successful")
            print(f"   📊 Result: {result}")
        else:
            print(f"   ❌ Webhook insert failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"🎯 TABLE VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_table_structure()