"""
Deploy Dual Indicator Schema via Web Endpoint
Uses your existing web server to deploy the database schema
"""

import requests
import json
import time

def create_deployment_endpoint_code():
    """Generate the deployment endpoint code to add to web_server.py"""
    
    endpoint_code = '''
# ============================================================================
# SCHEMA DEPLOYMENT ENDPOINT (Add this to web_server.py)
# ============================================================================

@app.route('/api/deploy-dual-schema', methods=['POST'])
def deploy_dual_schema():
    """Deploy dual indicator schema via web endpoint"""
    try:
        # Import database connection
        from database.railway_db import RailwayDB
        
        # Get database connection
        railway_db = RailwayDB()
        if not railway_db.conn:
            return jsonify({
                "success": False,
                "error": "Could not connect to database"
            }), 500
        
        cursor = railway_db.conn.cursor()
        
        # Schema SQL
        schema_sql = """
        -- Real-time price updates table (1-second TradingView data)
        CREATE TABLE IF NOT EXISTS realtime_prices (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL DEFAULT 'NQ',
            price DECIMAL(10,2) NOT NULL,
            timestamp BIGINT NOT NULL,
            session VARCHAR(20) NOT NULL,
            volume INTEGER DEFAULT 0,
            bid DECIMAL(10,2) DEFAULT 0,
            ask DECIMAL(10,2) DEFAULT 0,
            price_change DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Enhanced signals V2 table
        CREATE TABLE IF NOT EXISTS enhanced_signals_v2 (
            id SERIAL PRIMARY KEY,
            trade_uuid UUID DEFAULT gen_random_uuid(),
            signal_type VARCHAR(10) NOT NULL,
            session VARCHAR(20) NOT NULL,
            timestamp BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            signal_candle_open DECIMAL(10,2),
            signal_candle_high DECIMAL(10,2),
            signal_candle_low DECIMAL(10,2),
            signal_candle_close DECIMAL(10,2),
            signal_candle_volume INTEGER,
            requires_confirmation BOOLEAN DEFAULT TRUE,
            confirmation_condition VARCHAR(50),
            confirmation_target_price DECIMAL(10,2),
            confirmation_received BOOLEAN DEFAULT FALSE,
            confirmation_timestamp BIGINT,
            entry_price DECIMAL(10,2),
            entry_timestamp BIGINT,
            stop_loss_price DECIMAL(10,2),
            stop_loss_scenario VARCHAR(50),
            stop_loss_reasoning TEXT,
            pivot_count INTEGER DEFAULT 0,
            signal_is_pivot BOOLEAN DEFAULT FALSE,
            pivot_data JSONB,
            target_1r DECIMAL(10,2),
            target_2r DECIMAL(10,2),
            target_3r DECIMAL(10,2),
            target_5r DECIMAL(10,2),
            target_10r DECIMAL(10,2),
            target_20r DECIMAL(10,2),
            estimated_entry DECIMAL(10,2),
            risk_distance DECIMAL(10,2),
            current_mfe DECIMAL(10,4) DEFAULT 0,
            max_mfe DECIMAL(10,4) DEFAULT 0,
            status VARCHAR(30) DEFAULT 'awaiting_confirmation',
            automation_level VARCHAR(20) DEFAULT 'enhanced_v2',
            resolved BOOLEAN DEFAULT FALSE,
            resolution_type VARCHAR(20),
            resolution_price DECIMAL(10,2),
            resolution_timestamp BIGINT,
            final_mfe DECIMAL(10,4),
            market_context JSONB,
            raw_signal_data JSONB
        );
        
        -- Real-time MFE updates table
        CREATE TABLE IF NOT EXISTS realtime_mfe_updates (
            id SERIAL PRIMARY KEY,
            trade_uuid UUID NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            mfe_value DECIMAL(10,4) NOT NULL,
            is_new_high BOOLEAN DEFAULT FALSE,
            timestamp BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_realtime_prices_timestamp ON realtime_prices(timestamp);
        CREATE INDEX IF NOT EXISTS idx_realtime_prices_symbol ON realtime_prices(symbol);
        CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_uuid ON enhanced_signals_v2(trade_uuid);
        CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_status ON enhanced_signals_v2(status);
        CREATE INDEX IF NOT EXISTS idx_realtime_mfe_trade_uuid ON realtime_mfe_updates(trade_uuid);
        CREATE INDEX IF NOT EXISTS idx_realtime_mfe_timestamp ON realtime_mfe_updates(timestamp);
        """
        
        # Execute schema
        cursor.execute(schema_sql)
        railway_db.conn.commit()
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('realtime_prices', 'enhanced_signals_v2', 'realtime_mfe_updates')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # Deploy database functions
        functions_sql = """
        -- Function to process real-time price updates
        CREATE OR REPLACE FUNCTION process_realtime_price_update(
            p_symbol VARCHAR,
            p_price DECIMAL,
            p_timestamp BIGINT,
            p_session VARCHAR,
            p_volume INTEGER DEFAULT 0,
            p_bid DECIMAL DEFAULT 0,
            p_ask DECIMAL DEFAULT 0,
            p_change DECIMAL DEFAULT 0
        ) RETURNS JSONB AS $$
        DECLARE
            v_result JSONB;
            v_active_trades INTEGER;
        BEGIN
            INSERT INTO realtime_prices (
                symbol, price, timestamp, session, volume, bid, ask, price_change
            ) VALUES (
                p_symbol, p_price, p_timestamp, p_session, p_volume, p_bid, p_ask, p_change
            );
            
            SELECT COUNT(*) INTO v_active_trades
            FROM enhanced_signals_v2
            WHERE confirmation_received = TRUE
            AND resolved = FALSE
            AND entry_price IS NOT NULL;
            
            v_result := jsonb_build_object(
                'success', TRUE,
                'price_recorded', p_price,
                'active_trades_updated', v_active_trades,
                'timestamp', p_timestamp
            );
            
            RETURN v_result;
            
        EXCEPTION WHEN OTHERS THEN
            RETURN jsonb_build_object(
                'success', FALSE,
                'error', SQLERRM
            );
        END;
        $$ LANGUAGE plpgsql;
        """
        
        cursor.execute(functions_sql)
        railway_db.conn.commit()
        
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Dual indicator schema deployed successfully",
            "tables_created": table_names,
            "functions_deployed": ["process_realtime_price_update"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Schema deployment error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
'''
    
    return endpoint_code

def test_deployment_via_web(base_url="https://web-production-cd33.up.railway.app"):
    """Test the deployment via web endpoint"""
    
    try:
        print(f"🚀 Testing deployment via web endpoint: {base_url}")
        
        # Test the deployment endpoint
        response = requests.post(f"{base_url}/api/deploy-dual-schema", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Schema deployment successful!")
            print(f"   Tables created: {result.get('tables_created', [])}")
            print(f"   Functions deployed: {result.get('functions_deployed', [])}")
            return True
        else:
            print(f"❌ Deployment failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return False

def main():
    """Main deployment process"""
    
    print("🚀 Dual Indicator Schema Deployment via Web Endpoint")
    print("=" * 60)
    
    print("📋 Step 1: Add Deployment Endpoint to web_server.py")
    print("Copy and paste this code into your web_server.py file:")
    print("=" * 60)
    print(create_deployment_endpoint_code())
    print("=" * 60)
    
    print("\n📋 Step 2: Deploy to Railway")
    print("1. Add the above code to web_server.py")
    print("2. Commit and push to Railway:")
    print("   git add .")
    print("   git commit -m 'Add dual indicator schema deployment endpoint'")
    print("   git push origin main")
    
    print("\n📋 Step 3: Test Deployment")
    print("After Railway deployment completes, run:")
    print("   python deploy_via_web_endpoint.py test")
    
    # Check if user wants to test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🧪 Testing deployment...")
        success = test_deployment_via_web()
        
        if success:
            print("\n🎉 Dual Indicator System Ready!")
            print("✅ Database schema deployed")
            print("✅ Real-time price table created")
            print("✅ Enhanced signals V2 table ready")
            print("✅ MFE tracking system operational")
            
            print("\n📋 Next Steps:")
            print("1. Setup TradingView indicators:")
            print("   - Chart 1 (1-minute): enhanced_tradingview_indicator.pine")
            print("   - Chart 2 (1-second): tradingview_realtime_price_streamer.pine")
            print("2. Configure webhook URLs:")
            print("   - Signals: https://web-production-cd33.up.railway.app/api/live-signals-v2")
            print("   - Prices: https://web-production-cd33.up.railway.app/api/realtime-price")
            print("3. Test with live TradingView data")
        else:
            print("\n❌ Deployment test failed")
            print("Check Railway logs and ensure the endpoint was added correctly")

if __name__ == "__main__":
    main()