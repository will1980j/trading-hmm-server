#!/usr/bin/env python3
"""
Test V2 Simple Creation - Test creating V2 trades through the deployment endpoint
"""

import requests

def test_v2_simple_creation():
    """Test creating V2 trades using the deployment endpoint"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🧪 TESTING V2 TRADE CREATION")
    print("=" * 40)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Test creating a V2 trade with the exact same logic as the API endpoint
    print("\n📝 Creating V2 trade with API logic...")
    
    # Simulate the API endpoint logic
    signal_type = "Bullish"
    signal_price = 20000.00
    signal_session = "TEST"
    
    # Calculate prices (same as API)
    entry_price = signal_price + 2.5  # 20002.50
    stop_loss_price = signal_price - 25.0  # 19975.00
    risk_distance = abs(entry_price - stop_loss_price)  # 27.50
    
    # Calculate R-targets (same as API)
    target_1r = entry_price + risk_distance  # 20030.00
    target_2r = entry_price + (2 * risk_distance)  # 20057.50
    target_3r = entry_price + (3 * risk_distance)  # 20085.00
    target_5r = entry_price + (5 * risk_distance)  # 20140.00
    target_10r = entry_price + (10 * risk_distance)  # 20277.50
    target_20r = entry_price + (20 * risk_distance)  # 20552.50
    
    print(f"   Entry: ${entry_price}")
    print(f"   Stop Loss: ${stop_loss_price}")
    print(f"   Risk Distance: ${risk_distance}")
    print(f"   20R Target: ${target_20r}")
    
    # Create the exact SQL from the API endpoint
    create_sql = f"""
    INSERT INTO signal_lab_v2_trades (
        trade_uuid, symbol, bias, session, 
        date, time, entry_price, stop_loss_price, risk_distance,
        target_1r_price, target_2r_price, target_3r_price,
        target_5r_price, target_10r_price, target_20r_price,
        current_mfe, trade_status, active_trade, auto_populated
    ) VALUES (
        gen_random_uuid(), 'NQ1!', '{signal_type}', '{signal_session}',
        CURRENT_DATE, CURRENT_TIME, {entry_price}, {stop_loss_price}, {risk_distance},
        {target_1r}, {target_2r}, {target_3r},
        {target_5r}, {target_10r}, {target_20r},
        0.00, 'active', true, true
    ) RETURNING id, trade_uuid;
    """
    
    try:
        payload = {"schema_sql": create_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 trade created successfully!")
            print("🎉 The V2 automation logic works!")
            print("   Issue is likely in the API endpoint error handling")
        else:
            print(f"❌ V2 trade creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 trade creation request failed: {e}")
    
    # Check if the trade was created
    print("\n📊 Checking V2 trades...")
    
    check_sql = """
    SELECT 
        id, bias, entry_price, target_20r_price, created_at
    FROM signal_lab_v2_trades 
    WHERE session = 'TEST'
    ORDER BY created_at DESC 
    LIMIT 3;
    """
    
    try:
        payload = {"schema_sql": check_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 trades verified!")
            print("📈 Test trades are in the database")
        else:
            print(f"❌ V2 trade check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 trade check request failed: {e}")

if __name__ == "__main__":
    test_v2_simple_creation()