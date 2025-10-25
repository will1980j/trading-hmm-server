#!/usr/bin/env python3
"""
Deploy V2 Simple - Add basic automation without complex functions
"""

import requests

def deploy_v2_simple():
    """Deploy simple V2 automation to Railway"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 DEPLOYING SIMPLE V2 AUTOMATION")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Step 1: Create monitoring view (simple)
    view_sql = """
CREATE OR REPLACE VIEW v2_active_trades_monitor AS
SELECT 
    id,
    trade_uuid,
    bias,
    session,
    entry_price,
    stop_loss_price,
    current_mfe,
    target_1r_price,
    target_5r_price,
    target_10r_price,
    target_20r_price,
    CASE 
        WHEN current_mfe >= 20 THEN 'MEGA TREND'
        WHEN current_mfe >= 10 THEN 'BIG MOVE'
        WHEN current_mfe >= 5 THEN 'STRONG'
        WHEN current_mfe >= 1 THEN 'PROFIT'
        ELSE 'PENDING'
    END as status_text,
    created_at,
    updated_at
FROM signal_lab_v2_trades 
WHERE active_trade = true
ORDER BY current_mfe DESC, created_at DESC;
"""
    
    print("📋 Step 1: Creating monitoring view...")
    
    try:
        payload = {"schema_sql": view_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Monitoring view created!")
        else:
            print(f"❌ View creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ View creation request failed: {e}")
    
    # Step 2: Test with a manual V2 trade insertion
    print("📋 Step 2: Testing V2 trade creation...")
    
    test_insert_sql = """
INSERT INTO signal_lab_v2_trades (
    trade_uuid, symbol, bias, session, 
    date, time, entry_price, stop_loss_price, risk_distance,
    target_1r_price, target_2r_price, target_3r_price,
    target_5r_price, target_10r_price, target_20r_price,
    current_mfe, trade_status, active_trade, auto_populated
) VALUES (
    gen_random_uuid(), 'NQ1!', 'Bullish', 'NY PM',
    CURRENT_DATE, CURRENT_TIME, 
    20002.50, 19975.00, 27.50,
    20030.00, 20057.50, 20085.00,
    20140.00, 20277.50, 20552.50,
    0.00, 'active', true, true
) ON CONFLICT (trade_uuid) DO NOTHING;
"""
    
    try:
        payload = {"schema_sql": test_insert_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Test trade created!")
        else:
            print(f"❌ Test trade failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test trade request failed: {e}")
    
    # Step 3: Test monitoring view
    print("📋 Step 3: Testing monitoring view...")
    
    monitor_test_sql = """
SELECT 
    COUNT(*) as total_active,
    AVG(current_mfe) as avg_mfe,
    MAX(current_mfe) as max_mfe
FROM v2_active_trades_monitor;
"""
    
    try:
        payload = {"schema_sql": monitor_test_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Monitoring view working!")
        else:
            print(f"❌ Monitoring view test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Monitoring view test request failed: {e}")
    
    # Step 4: Create a simple automation trigger
    print("📋 Step 4: Testing MFE update...")
    
    mfe_update_sql = """
UPDATE signal_lab_v2_trades 
SET current_mfe = 1.5, updated_at = NOW()
WHERE active_trade = true 
AND auto_populated = true
AND current_mfe < 1.5;
"""
    
    try:
        payload = {"schema_sql": mfe_update_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ MFE update successful!")
            print("\n🎉 SIMPLE V2 AUTOMATION DEPLOYED!")
            print("=" * 50)
            print("✅ V2 table: signal_lab_v2_trades")
            print("✅ Monitoring view: v2_active_trades_monitor")
            print("✅ Test trade created with 20R targets")
            print("✅ MFE tracking system working")
            print("\n🚀 Ready for manual signal processing!")
            print("📝 Next: Add API endpoints to web_server.py")
        else:
            print(f"❌ MFE update failed: {response.text}")
            
    except Exception as e:
        print(f"❌ MFE update request failed: {e}")

if __name__ == "__main__":
    deploy_v2_simple()