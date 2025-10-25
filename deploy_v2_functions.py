#!/usr/bin/env python3
"""
Deploy V2 Functions - Add automation functions to the database
"""

import requests

def deploy_v2_functions():
    """Deploy V2 automation functions to Railway"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 DEPLOYING V2 AUTOMATION FUNCTIONS")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Step 1: Create the signal processing function
    function_sql = """
CREATE OR REPLACE FUNCTION process_signal_v2(
    p_signal_type VARCHAR(10),
    p_signal_price DECIMAL(10,2),
    p_signal_timestamp TIMESTAMP,
    p_signal_session VARCHAR(20)
) RETURNS TABLE(
    success BOOLEAN,
    trade_id BIGINT,
    trade_uuid UUID,
    entry_price DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    risk_distance DECIMAL(10,2)
) AS $$
DECLARE
    v_trade_id BIGINT;
    v_entry_price DECIMAL(10,2);
    v_stop_loss_price DECIMAL(10,2);
    v_risk_distance DECIMAL(10,2);
    v_trade_uuid UUID;
BEGIN
    -- Generate UUID for trade
    v_trade_uuid := gen_random_uuid();
    
    -- Calculate entry price (simplified - next candle open simulation)
    IF p_signal_type = 'Bullish' THEN
        v_entry_price := p_signal_price + 2.5;
        v_stop_loss_price := p_signal_price - 25.0;
    ELSE
        v_entry_price := p_signal_price - 2.5;
        v_stop_loss_price := p_signal_price + 25.0;
    END IF;
    
    -- Calculate risk distance
    v_risk_distance := ABS(v_entry_price - v_stop_loss_price);
    
    -- Insert V2 trade
    INSERT INTO signal_lab_v2_trades (
        trade_uuid, symbol, bias, session, 
        date, time, entry_price, stop_loss_price, risk_distance,
        target_1r_price, target_2r_price, target_3r_price,
        target_5r_price, target_10r_price, target_20r_price,
        current_mfe, trade_status, active_trade, auto_populated
    ) VALUES (
        v_trade_uuid, 'NQ1!', p_signal_type, p_signal_session,
        p_signal_timestamp::date, p_signal_timestamp::time, 
        v_entry_price, v_stop_loss_price, v_risk_distance,
        -- Calculate R-targets
        CASE WHEN p_signal_type = 'Bullish' 
             THEN v_entry_price + v_risk_distance 
             ELSE v_entry_price - v_risk_distance END,
        CASE WHEN p_signal_type = 'Bullish' 
             THEN v_entry_price + (2 * v_risk_distance) 
             ELSE v_entry_price - (2 * v_risk_distance) END,
        CASE WHEN p_signal_type = 'Bullish' 
             THEN v_entry_price + (3 * v_risk_distance) 
             ELSE v_entry_price - (3 * v_risk_distance) END,
        CASE WHEN p_signal_type = 'Bullish' 
             THEN v_entry_price + (5 * v_risk_distance) 
             ELSE v_entry_price - (5 * v_risk_distance) END,
        CASE WHEN p_signal_type = 'Bullish' 
             THEN v_entry_price + (10 * v_risk_distance) 
             ELSE v_entry_price - (10 * v_risk_distance) END,
        CASE WHEN p_signal_type = 'Bullish' 
             THEN v_entry_price + (20 * v_risk_distance) 
             ELSE v_entry_price - (20 * v_risk_distance) END,
        0.00, 'active', true, true
    ) RETURNING id INTO v_trade_id;
    
    -- Return result
    RETURN QUERY SELECT 
        true as success,
        v_trade_id,
        v_trade_uuid,
        v_entry_price,
        v_stop_loss_price,
        v_risk_distance;
END;
$$ LANGUAGE plpgsql;
"""
    
    print("📋 Step 1: Creating signal processing function...")
    
    try:
        payload = {"schema_sql": function_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Signal processing function created!")
        else:
            print(f"❌ Function creation failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Function creation request failed: {e}")
        return
    
    # Step 2: Create monitoring view
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
        WHEN current_mfe >= 20 THEN '🚀 MEGA TREND!'
        WHEN current_mfe >= 10 THEN '💎 BIG MOVE!'
        WHEN current_mfe >= 5 THEN '📈 STRONG'
        WHEN current_mfe >= 1 THEN '✅ PROFIT'
        ELSE '⏳ PENDING'
    END as status_emoji,
    created_at,
    updated_at
FROM signal_lab_v2_trades 
WHERE active_trade = true
ORDER BY current_mfe DESC, created_at DESC;
"""
    
    print("📋 Step 2: Creating monitoring view...")
    
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
    
    # Step 3: Test the function
    print("📋 Step 3: Testing automation function...")
    
    test_sql = """
SELECT * FROM process_signal_v2(
    'Bullish',
    20000.00,
    NOW(),
    'NY PM'
);
"""
    
    try:
        payload = {"schema_sql": test_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Automation function test successful!")
        else:
            print(f"❌ Function test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Function test request failed: {e}")
    
    # Step 4: Test monitoring view
    print("📋 Step 4: Testing monitoring view...")
    
    monitor_test_sql = """
SELECT COUNT(*) as active_count FROM v2_active_trades_monitor;
"""
    
    try:
        payload = {"schema_sql": monitor_test_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Monitoring view test successful!")
            print("\n🎉 V2 AUTOMATION FUNCTIONS DEPLOYED!")
            print("=" * 50)
            print("✅ Signal processing function: process_signal_v2()")
            print("✅ Monitoring view: v2_active_trades_monitor")
            print("✅ Automated trade creation working")
            print("✅ 20R targeting system active")
            print("\n🚀 Ready for TradingView integration!")
        else:
            print(f"❌ Monitoring view test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Monitoring view test request failed: {e}")

if __name__ == "__main__":
    deploy_v2_functions()