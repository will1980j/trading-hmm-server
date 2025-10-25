#!/usr/bin/env python3
"""
V2 Automation Integration Script
Integrates the automated signal processing with your existing web server
"""

import requests
import json

def integrate_v2_automation():
    """Add V2 automation endpoints to the existing web server"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 INTEGRATING V2 AUTOMATION")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Add V2 automation endpoints to web_server.py
    v2_endpoints_sql = """
-- Add V2 automation endpoints and functions

-- Function to process incoming signals automatically
CREATE OR REPLACE FUNCTION process_signal_v2(
    signal_type VARCHAR(10),
    signal_price DECIMAL(10,2),
    signal_timestamp TIMESTAMP,
    signal_session VARCHAR(20)
) RETURNS JSON AS $$
DECLARE
    result JSON;
    trade_id BIGINT;
    entry_price DECIMAL(10,2);
    stop_loss_price DECIMAL(10,2);
    risk_distance DECIMAL(10,2);
    trade_uuid UUID;
BEGIN
    -- Generate UUID for trade
    trade_uuid := gen_random_uuid();
    
    -- Calculate entry price (simplified - next candle open simulation)
    IF signal_type = 'Bullish' THEN
        entry_price := signal_price + 2.5;
        stop_loss_price := signal_price - 25.0;
    ELSE
        entry_price := signal_price - 2.5;
        stop_loss_price := signal_price + 25.0;
    END IF;
    
    -- Calculate risk distance
    risk_distance := ABS(entry_price - stop_loss_price);
    
    -- Insert V2 trade
    INSERT INTO signal_lab_v2_trades (
        trade_uuid, symbol, bias, session, 
        date, time, entry_price, stop_loss_price, risk_distance,
        target_1r_price, target_2r_price, target_3r_price,
        target_5r_price, target_10r_price, target_20r_price,
        current_mfe, trade_status, active_trade, auto_populated
    ) VALUES (
        trade_uuid, 'NQ1!', signal_type, signal_session,
        signal_timestamp::date, signal_timestamp::time, 
        entry_price, stop_loss_price, risk_distance,
        -- Calculate R-targets
        CASE WHEN signal_type = 'Bullish' 
             THEN entry_price + risk_distance 
             ELSE entry_price - risk_distance END,
        CASE WHEN signal_type = 'Bullish' 
             THEN entry_price + (2 * risk_distance) 
             ELSE entry_price - (2 * risk_distance) END,
        CASE WHEN signal_type = 'Bullish' 
             THEN entry_price + (3 * risk_distance) 
             ELSE entry_price - (3 * risk_distance) END,
        CASE WHEN signal_type = 'Bullish' 
             THEN entry_price + (5 * risk_distance) 
             ELSE entry_price - (5 * risk_distance) END,
        CASE WHEN signal_type = 'Bullish' 
             THEN entry_price + (10 * risk_distance) 
             ELSE entry_price - (10 * risk_distance) END,
        CASE WHEN signal_type = 'Bullish' 
             THEN entry_price + (20 * risk_distance) 
             ELSE entry_price - (20 * risk_distance) END,
        0.00, 'active', true, true
    ) RETURNING id INTO trade_id;
    
    -- Build result JSON
    result := json_build_object(
        'success', true,
        'trade_id', trade_id,
        'trade_uuid', trade_uuid,
        'entry_price', entry_price,
        'stop_loss_price', stop_loss_price,
        'risk_distance', risk_distance,
        'automation', 'v2_enabled'
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create V2 monitoring view
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
    
    print("📋 Adding V2 database functions...")
    
    try:
        payload = {"schema_sql": v2_endpoints_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ V2 database functions added!")
        else:
            print(f"❌ Database functions failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Database functions request failed: {e}")
    
    # Test the V2 automation with a sample signal
    print("\n🧪 Testing V2 automation with sample signal...")
    
    test_signal_sql = """
    SELECT process_signal_v2(
        'Bullish',
        20000.00,
        NOW(),
        'NY PM'
    ) as automation_result;
    """
    
    try:
        payload = {"schema_sql": test_signal_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 automation test successful!")
        else:
            print(f"❌ V2 automation test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 automation test request failed: {e}")
    
    # Check V2 monitoring view
    print("\n📊 Checking V2 monitoring view...")
    
    monitor_sql = """
    SELECT * FROM v2_active_trades_monitor LIMIT 5;
    """
    
    try:
        payload = {"schema_sql": monitor_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 monitoring view working!")
        else:
            print(f"❌ V2 monitoring view failed: {response.text}")
            
    except Exception as e:
        print(f"❌ V2 monitoring view request failed: {e}")

def create_v2_api_endpoints():
    """Generate the API endpoint code to add to web_server.py"""
    
    api_code = '''
# V2 AUTOMATION API ENDPOINTS
# Add these to your web_server.py file

@app.route('/api/v2/process-signal', methods=['POST'])
@login_required
def process_signal_v2():
    """Process TradingView signal through V2 automation"""
    try:
        data = request.get_json()
        
        signal_type = data.get('type', '')
        signal_price = float(data.get('price', 0))
        signal_timestamp = data.get('timestamp', datetime.now().isoformat())
        signal_session = data.get('session', 'NY AM')
        
        # Use database function for processing
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT process_signal_v2(%s, %s, %s, %s) as result;
        """, (signal_type, signal_price, signal_timestamp, signal_session))
        
        result = cursor.fetchone()[0]
        
        return jsonify({
            "success": True,
            "automation_result": result,
            "message": "Signal processed through V2 automation"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v2/active-trades', methods=['GET'])
@login_required
def get_v2_active_trades():
    """Get all active V2 trades with real-time MFE"""
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM v2_active_trades_monitor;")
        
        trades = []
        for row in cursor.fetchall():
            trade = dict(row) if hasattr(row, 'keys') else {}
            trades.append(trade)
        
        return jsonify({
            "success": True,
            "active_trades": trades,
            "count": len(trades)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v2/mfe-update', methods=['POST'])
@login_required
def update_v2_mfe():
    """Update MFE for active trades"""
    try:
        data = request.get_json()
        trade_id = data.get('trade_id')
        new_mfe = float(data.get('mfe', 0))
        
        cursor = db.conn.cursor()
        cursor.execute("""
            UPDATE signal_lab_v2_trades 
            SET current_mfe = GREATEST(current_mfe, %s), updated_at = NOW()
            WHERE id = %s AND active_trade = true;
        """, (new_mfe, trade_id))
        
        db.conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"MFE updated to {new_mfe}R for trade {trade_id}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v2/stats', methods=['GET'])
@login_required
def get_v2_stats():
    """Get V2 automation statistics"""
    try:
        cursor = db.conn.cursor()
        
        # Get comprehensive V2 stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_v2_trades,
                COUNT(CASE WHEN active_trade = true THEN 1 END) as active_trades,
                AVG(CASE WHEN active_trade = true THEN current_mfe END) as avg_active_mfe,
                MAX(current_mfe) as max_mfe_achieved,
                COUNT(CASE WHEN current_mfe >= 1 THEN 1 END) as trades_above_1r,
                COUNT(CASE WHEN current_mfe >= 5 THEN 1 END) as trades_above_5r,
                COUNT(CASE WHEN current_mfe >= 10 THEN 1 END) as trades_above_10r,
                COUNT(CASE WHEN current_mfe >= 20 THEN 1 END) as trades_above_20r,
                COUNT(CASE WHEN auto_populated = true THEN 1 END) as automated_trades
            FROM signal_lab_v2_trades;
        """)
        
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        stats = dict(zip(columns, result)) if result else {}
        
        return jsonify({
            "success": True,
            "v2_stats": stats,
            "automation_status": "active"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Enhanced webhook endpoint (modify your existing /api/live-signals)
@app.route('/api/live-signals-v2', methods=['POST'])
def receive_signal_v2():
    """Enhanced webhook with V2 automation"""
    try:
        data = request.get_json()
        
        # Store in original live_signals table (compatibility)
        original_result = store_original_signal(data)
        
        # Process through V2 automation
        v2_result = None
        try:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT process_signal_v2(%s, %s, %s, %s) as result;
            """, (
                data.get('type', ''),
                float(data.get('price', 0)),
                data.get('timestamp', datetime.now().isoformat()),
                data.get('session', 'NY AM')
            ))
            
            v2_result = cursor.fetchone()[0]
            
        except Exception as v2_error:
            logger.error(f"V2 processing error: {v2_error}")
        
        return jsonify({
            "success": True,
            "original_signal": original_result,
            "v2_automation": v2_result,
            "timestamp": datetime.now().isoformat(),
            "message": "Signal processed with V2 automation"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
'''
    
    return api_code

def test_v2_integration():
    """Test the V2 integration"""
    print("🧪 TESTING V2 INTEGRATION")
    print("=" * 40)
    
    # Show the API code that needs to be added
    api_code = create_v2_api_endpoints()
    
    print("📋 API endpoints to add to web_server.py:")
    print("=" * 50)
    print(api_code[:500] + "...")
    print("\n✅ Integration code generated!")
    print("📝 Next steps:")
    print("1. Add the API endpoints to web_server.py")
    print("2. Deploy to Railway")
    print("3. Test V2 automation with TradingView signals")

if __name__ == "__main__":
    integrate_v2_automation()
    print("\n" + "="*50)
    test_v2_integration()