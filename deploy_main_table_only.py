#!/usr/bin/env python3

import requests

def deploy_main_table():
    """Deploy just the main V2 table first"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 DEPLOYING MAIN V2 TABLE")
    print("=" * 40)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Create just the main V2 table with essential columns
    main_table_sql = """
-- Signal Lab V2 Main Table
CREATE TABLE IF NOT EXISTS signal_lab_v2_trades (
    id BIGSERIAL PRIMARY KEY,
    trade_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    
    -- Basic trade info (from V1)
    symbol VARCHAR(10) DEFAULT 'NQ1!',
    bias VARCHAR(10) NOT NULL,
    session VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    
    -- Enhanced price tracking
    entry_price DECIMAL(10,2),
    stop_loss_price DECIMAL(10,2),
    risk_distance DECIMAL(10,2),
    
    -- 20R targeting system
    target_1r_price DECIMAL(10,2),
    target_2r_price DECIMAL(10,2),
    target_3r_price DECIMAL(10,2),
    target_5r_price DECIMAL(10,2),
    target_10r_price DECIMAL(10,2),
    target_20r_price DECIMAL(10,2),
    
    -- MFE tracking
    current_mfe DECIMAL(5,2) DEFAULT 0.00,
    final_mfe DECIMAL(5,2),
    
    -- Trade status
    trade_status VARCHAR(20) DEFAULT 'pending',
    active_trade BOOLEAN DEFAULT true,
    
    -- Automation flags
    auto_populated BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Basic indexes
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_date ON signal_lab_v2_trades(date);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_status ON signal_lab_v2_trades(trade_status);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_active ON signal_lab_v2_trades(active_trade);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_uuid ON signal_lab_v2_trades(trade_uuid);
"""
    
    print("📋 Creating main V2 table...")
    print(f"   Size: {len(main_table_sql)} characters")
    
    try:
        payload = {"schema_sql": main_table_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MAIN TABLE CREATED SUCCESSFULLY!")
            print(f"📊 V1 Trade Count: {result.get('v1_trade_count', 'Unknown')}")
            print(f"📋 Tables Created: {result.get('tables_created', [])}")
            print(f"💬 Message: {result.get('message', 'No message')}")
            
            # Test the table
            print(f"\n🧪 Testing table creation...")
            test_insert_sql = """
            INSERT INTO signal_lab_v2_trades (bias, session, date, time, entry_price, stop_loss_price)
            VALUES ('Bullish', 'NY AM', CURRENT_DATE, CURRENT_TIME, 20000.00, 19975.00)
            ON CONFLICT DO NOTHING;
            """
            
            test_payload = {"schema_sql": test_insert_sql}
            test_response = session.post(
                f"{base_url}/api/deploy-signal-lab-v2",
                json=test_payload,
                timeout=30
            )
            
            if test_response.status_code == 200:
                print("✅ Table is working - can insert test data!")
            else:
                print(f"⚠️ Table created but test insert failed: {test_response.text}")
            
        else:
            print(f"❌ MAIN TABLE CREATION FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    deploy_main_table()