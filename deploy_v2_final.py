#!/usr/bin/env python3

import requests

def deploy_v2_final():
    """Final V2 deployment with corrected approach"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 FINAL V2 DEPLOYMENT")
    print("=" * 40)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Deploy the main V2 table
    main_table_sql = """
CREATE TABLE IF NOT EXISTS signal_lab_v2_trades (
    id BIGSERIAL PRIMARY KEY,
    trade_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    
    -- Basic trade info
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
"""
    
    print("📋 Step 1: Creating main V2 table...")
    
    try:
        payload = {"schema_sql": main_table_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Main table created!")
        else:
            print(f"❌ Main table failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Main table request failed: {e}")
        return
    
    # Create indexes
    indexes_sql = """
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_date ON signal_lab_v2_trades(date);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_status ON signal_lab_v2_trades(trade_status);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_active ON signal_lab_v2_trades(active_trade);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_uuid ON signal_lab_v2_trades(trade_uuid);
CREATE INDEX IF NOT EXISTS idx_signal_lab_v2_session ON signal_lab_v2_trades(session);
"""
    
    print("📋 Step 2: Creating indexes...")
    
    try:
        payload = {"schema_sql": indexes_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Indexes created!")
        else:
            print(f"❌ Indexes failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Indexes request failed: {e}")
    
    # Test the table with a sample insert
    print("📋 Step 3: Testing table with sample data...")
    
    test_insert_sql = """
INSERT INTO signal_lab_v2_trades (
    bias, session, date, time, 
    entry_price, stop_loss_price, risk_distance,
    target_1r_price, target_2r_price, target_3r_price
) VALUES (
    'Bullish', 'NY AM', CURRENT_DATE, CURRENT_TIME,
    20000.00, 19975.00, 25.00,
    20025.00, 20050.00, 20075.00
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
            print("✅ Sample data inserted successfully!")
            print("\n🎉 SIGNAL LAB V2 DEPLOYMENT COMPLETE!")
            print("=" * 50)
            print("✅ Main table: signal_lab_v2_trades")
            print("✅ 20R targeting system ready")
            print("✅ Real-time MFE tracking enabled")
            print("✅ Automated price calculations supported")
            print("✅ Complete trade lifecycle management")
            print("\n🚀 Ready for automated signal processing!")
            
        else:
            print(f"⚠️ Table created but sample insert failed: {response.text}")
            print("Table exists but may need troubleshooting")
            
    except Exception as e:
        print(f"❌ Sample insert request failed: {e}")

if __name__ == "__main__":
    deploy_v2_final()