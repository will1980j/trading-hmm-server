#!/usr/bin/env python3
"""
Test V2 Database Direct - Check if V2 database is accessible
"""

import requests

def test_v2_database_direct():
    """Test V2 database access directly"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🔍 TESTING V2 DATABASE ACCESS")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Test 1: Check if V2 table exists
    print("\n📋 Test 1: Checking V2 table existence...")
    
    check_table_sql = """
    SELECT COUNT(*) as count FROM signal_lab_v2_trades;
    """
    
    try:
        payload = {"schema_sql": check_table_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 table accessible!")
        else:
            print(f"❌ V2 table check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 table check request failed: {e}")
    
    # Test 2: Try to insert a V2 trade manually
    print("\n📝 Test 2: Manual V2 trade insertion...")
    
    insert_sql = """
    INSERT INTO signal_lab_v2_trades (
        trade_uuid, symbol, bias, session, 
        date, time, entry_price, stop_loss_price, risk_distance,
        target_1r_price, target_2r_price, target_3r_price,
        target_5r_price, target_10r_price, target_20r_price,
        current_mfe, trade_status, active_trade, auto_populated
    ) VALUES (
        gen_random_uuid(), 'NQ1!', 'Bullish', 'TEST',
        CURRENT_DATE, CURRENT_TIME, 
        20002.50, 19975.00, 27.50,
        20030.00, 20057.50, 20085.00,
        20140.00, 20277.50, 20552.50,
        0.00, 'active', true, true
    ) RETURNING id, trade_uuid;
    """
    
    try:
        payload = {"schema_sql": insert_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Manual V2 trade insertion successful!")
        else:
            print(f"❌ Manual insertion failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Manual insertion request failed: {e}")
    
    # Test 3: Check V2 monitoring view
    print("\n📊 Test 3: V2 monitoring view...")
    
    view_sql = """
    SELECT COUNT(*) as active_count FROM v2_active_trades_monitor;
    """
    
    try:
        payload = {"schema_sql": view_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 monitoring view accessible!")
        else:
            print(f"❌ V2 monitoring view failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 monitoring view request failed: {e}")
    
    # Test 4: Check what's in V2 table
    print("\n📋 Test 4: V2 table contents...")
    
    contents_sql = """
    SELECT 
        id, bias, entry_price, target_20r_price, current_mfe, active_trade
    FROM signal_lab_v2_trades 
    ORDER BY created_at DESC 
    LIMIT 5;
    """
    
    try:
        payload = {"schema_sql": contents_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 table contents accessible!")
        else:
            print(f"❌ V2 table contents failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 table contents request failed: {e}")

if __name__ == "__main__":
    test_v2_database_direct()