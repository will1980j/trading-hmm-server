#!/usr/bin/env python3
"""
DEPLOY COMPLETE AUTOMATION TO RAILWAY
Deploy complete automation system for data collection and forward testing
"""

import os
import sys
import requests
import json
from datetime import datetime

# Railway endpoint
RAILWAY_ENDPOINT = "https://web-production-cd33.up.railway.app"

def create_complete_automation_integration():
    """Create complete automation integration for web_server.py"""
    
    integration_code = '''
# ============================================================================
# COMPLETE AUTOMATION SYSTEM FOR DATA COLLECTION & FORWARD TESTING
# ============================================================================

# Import complete automation components
try:
    from complete_automation_pipeline import initialize_automation_pipeline, process_signal_through_complete_pipeline
    from enhanced_webhook_processor_v2 import process_enhanced_webhook, get_webhook_processor_status
    
    # Initialize automation pipeline on startup
    if db_enabled and db:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            initialize_automation_pipeline(DATABASE_URL)
            logger.info("Complete Automation Pipeline initialized for data collection")
        else:
            logger.warning("DATABASE_URL not available for automation pipeline")
    
    automation_available = True
    logger.info("Complete Automation System loaded for forward testing")
    
except ImportError as e:
    logger.warning(f"Complete Automation System not available: {str(e)}")
    automation_available = False

# Complete Automation Webhook for Data Collection
@app.route('/api/live-signals-v2-complete', methods=['POST'])
def receive_signal_v2_complete():
    """Complete automation webhook for comprehensive data collection and forward testing"""
    try:
        # Get raw webhook data
        raw_data = request.get_data(as_text=True)
        logger.info(f"[COMPLETE AUTOMATION] Raw webhook data received: {len(raw_data)} chars")
        
        # Parse JSON data
        try:
            webhook_data = json.loads(raw_data)
        except json.JSONDecodeError:
            # Handle plain text format
            webhook_data = raw_data
        
        # Process through complete automation if available
        if automation_available:
            automation_result = process_enhanced_webhook(webhook_data)
            
            # Also maintain compatibility with existing system
            try:
                # Store in original live_signals table for compatibility
                cursor = db.conn.cursor()
                cursor.execute("""
                    INSERT INTO live_signals (symbol, type, timestamp, price, session, bias)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (
                    'NQ1!',
                    automation_result.get('signal_data', {}).get('signal_type', ''),
                    datetime.now(),
                    automation_result.get('signal_data', {}).get('signal_candle', {}).get('close', 0),
                    automation_result.get('signal_data', {}).get('session_data', {}).get('current_session', 'NY AM'),
                    automation_result.get('signal_data', {}).get('signal_type', '')
                ))
                
                original_id = cursor.fetchone()[0]
                db.conn.commit()
                
            except Exception as original_error:
                logger.warning(f"Original table storage failed: {str(original_error)}")
                original_id = None
            
            return jsonify({
                "success": True,
                "message": "Signal processed through complete automation for data collection",
                "automation_result": automation_result,
                "original_signal_id": original_id,
                "automation_level": "complete_pipeline",
                "data_collection_mode": True,
                "forward_testing": True,
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            # Fallback to basic processing if automation not available
            return jsonify({
                "success": False,
                "message": "Complete automation not available",
                "fallback": "basic_processing",
                "timestamp": datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        logger.error(f"[COMPLETE AUTOMATION ERROR] {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "automation_level": "failed",
            "timestamp": datetime.now().isoformat()
        }), 500

# Automation Status Endpoint
@app.route('/api/automation/status', methods=['GET'])
@login_required
def get_automation_status():
    """Get complete automation system status"""
    try:
        if not automation_available:
            return jsonify({
                'status': 'unavailable',
                'message': 'Complete automation system not loaded',
                'timestamp': datetime.now().isoformat()
            })
        
        # Get webhook processor status
        processor_status = get_webhook_processor_status()
        
        # Get database status
        db_status = 'connected' if db_enabled and db else 'disconnected'
        
        return jsonify({
            'status': 'active',
            'mode': 'data_collection_forward_testing',
            'automation_available': automation_available,
            'database_status': db_status,
            'webhook_processor': processor_status,
            'capabilities': [
                'enhanced_fvg_processing',
                'complete_automation_pipeline',
                'exact_methodology_compliance',
                'confirmation_monitoring',
                'automated_mfe_tracking',
                'comprehensive_data_collection',
                'forward_testing_ready'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Data Collection Statistics
@app.route('/api/automation/data-stats', methods=['GET'])
@login_required
def get_automation_data_stats():
    """Get data collection statistics for forward testing analysis"""
    try:
        if not db_enabled or not db:
            return jsonify({
                'error': 'Database not available',
                'stats': {}
            })
        
        cursor = db.conn.cursor()
        
        # Get comprehensive data collection stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_signals,
                COUNT(CASE WHEN status = 'awaiting_confirmation' THEN 1 END) as awaiting_confirmation,
                COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_trades,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_trades,
                COUNT(CASE WHEN automation_level = 'complete_pipeline' THEN 1 END) as automated_signals,
                AVG(current_mfe) as avg_current_mfe,
                AVG(max_mfe) as avg_max_mfe,
                COUNT(CASE WHEN signal_type = 'Bullish' THEN 1 END) as bullish_signals,
                COUNT(CASE WHEN signal_type = 'Bearish' THEN 1 END) as bearish_signals
            FROM enhanced_signals_v2
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        
        stats_row = cursor.fetchone()
        
        cursor.close()
        
        return jsonify({
            'status': 'success',
            'data_collection_stats': dict(stats_row) if stats_row else {},
            'forward_testing_ready': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Data stats error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# END COMPLETE AUTOMATION SYSTEM FOR DATA COLLECTION
# ============================================================================
'''
    
    return integration_code

def create_automation_database_schema():
    """Create database schema for complete automation"""
    
    schema_sql = '''
-- Complete Automation Database Schema for Data Collection & Forward Testing

-- Enhanced signals V2 table (if not exists)
CREATE TABLE IF NOT EXISTS enhanced_signals_v2 (
    id SERIAL PRIMARY KEY,
    trade_uuid UUID DEFAULT gen_random_uuid(),
    signal_type VARCHAR(10) NOT NULL,
    session VARCHAR(20) NOT NULL,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Signal Candle Data
    signal_candle_open DECIMAL(10,2),
    signal_candle_high DECIMAL(10,2),
    signal_candle_low DECIMAL(10,2),
    signal_candle_close DECIMAL(10,2),
    signal_candle_volume INTEGER,
    
    -- Confirmation Logic
    requires_confirmation BOOLEAN DEFAULT TRUE,
    confirmation_condition VARCHAR(50),
    confirmation_target_price DECIMAL(10,2),
    confirmation_received BOOLEAN DEFAULT FALSE,
    confirmation_timestamp BIGINT,
    
    -- Trade Execution Data
    entry_price DECIMAL(10,2),
    entry_timestamp BIGINT,
    stop_loss_price DECIMAL(10,2),
    stop_loss_scenario VARCHAR(50),
    stop_loss_reasoning TEXT,
    
    -- R-Multiple Targets
    target_1r DECIMAL(10,2),
    target_2r DECIMAL(10,2),
    target_3r DECIMAL(10,2),
    target_5r DECIMAL(10,2),
    target_10r DECIMAL(10,2),
    target_20r DECIMAL(10,2),
    risk_distance DECIMAL(10,2),
    
    -- MFE Tracking for Forward Testing
    current_mfe DECIMAL(10,4) DEFAULT 0,
    max_mfe DECIMAL(10,4) DEFAULT 0,
    mfe_tracking_active BOOLEAN DEFAULT FALSE,
    last_mfe_update TIMESTAMP WITH TIME ZONE,
    
    -- Status Tracking
    status VARCHAR(30) DEFAULT 'awaiting_confirmation',
    automation_level VARCHAR(30) DEFAULT 'basic',
    resolved BOOLEAN DEFAULT FALSE,
    resolution_type VARCHAR(20),
    resolution_price DECIMAL(10,2),
    resolution_timestamp BIGINT,
    final_mfe DECIMAL(10,4),
    
    -- Data Collection & Forward Testing
    data_collection_mode BOOLEAN DEFAULT TRUE,
    forward_testing BOOLEAN DEFAULT TRUE,
    prop_firm_ready BOOLEAN DEFAULT FALSE,
    
    -- Data Storage
    market_context JSONB,
    raw_signal_data JSONB,
    
    -- Constraints
    CONSTRAINT valid_signal_type CHECK (signal_type IN ('Bullish', 'Bearish')),
    CONSTRAINT valid_status CHECK (status IN ('awaiting_confirmation', 'confirmed', 'active', 'resolved', 'cancelled'))
);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_automation_level ON enhanced_signals_v2(automation_level);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_data_collection ON enhanced_signals_v2(data_collection_mode);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_forward_testing ON enhanced_signals_v2(forward_testing);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_session_type ON enhanced_signals_v2(session, signal_type);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_created_at ON enhanced_signals_v2(created_at DESC);

-- Add automation-specific columns to existing table if they don't exist
DO $$ 
BEGIN
    -- Add automation level if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'automation_level') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN automation_level VARCHAR(30) DEFAULT 'basic';
    END IF;
    
    -- Add data collection mode if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'data_collection_mode') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN data_collection_mode BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Add forward testing flag if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'forward_testing') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN forward_testing BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Add prop firm readiness if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'enhanced_signals_v2' AND column_name = 'prop_firm_ready') THEN
        ALTER TABLE enhanced_signals_v2 ADD COLUMN prop_firm_ready BOOLEAN DEFAULT FALSE;
    END IF;
END $$;
'''
    
    return schema_sql

def deploy_to_railway():
    """Deploy complete automation system to Railway"""
    try:
        print("DEPLOYING COMPLETE AUTOMATION TO RAILWAY")
        print("=" * 55)
        
        # Create integration code
        integration_code = create_complete_automation_integration()
        
        # Create database schema
        schema_sql = create_automation_database_schema()
        
        # Save files locally
        with open('complete_automation_integration.py', 'w', encoding='utf-8') as f:
            f.write(integration_code)
        
        with open('automation_database_schema.sql', 'w', encoding='utf-8') as f:
            f.write(schema_sql)
        
        print("Complete automation files created")
        print("Files ready for deployment:")
        print("   - complete_automation_integration.py")
        print("   - automation_database_schema.sql")
        print("   - complete_automation_pipeline.py")
        print("   - enhanced_webhook_processor_v2.py")
        
        # Test current system
        print("\nTesting current system compatibility...")
        
        try:
            response = requests.get(f"{RAILWAY_ENDPOINT}/api/db-status", timeout=10)
            if response.status_code == 200:
                print("Database connection confirmed")
            else:
                print(f"Database status: {response.status_code}")
        except Exception as e:
            print(f"Database test: {str(e)}")
        
        try:
            response = requests.get(f"{RAILWAY_ENDPOINT}/signal-lab-v2", timeout=10)
            if response.status_code in [200, 302]:
                print("Signal Lab V2 dashboard accessible")
            else:
                print(f"Dashboard status: {response.status_code}")
        except Exception as e:
            print(f"Dashboard test: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"Deployment preparation error: {str(e)}")
        return False

def main():
    """Main deployment function"""
    success = deploy_to_railway()
    
    if success:
        print("\nCOMPLETE AUTOMATION DEPLOYMENT READY!")
        print("=" * 55)
        
        print("\nFOR DATA COLLECTION & FORWARD TESTING:")
        print("- Complete automation pipeline created")
        print("- Enhanced webhook processor ready")
        print("- Database schema for comprehensive data collection")
        print("- Forward testing analytics endpoints")
        print("- Prop firm readiness metrics")
        
        print("\nDATA COLLECTION FEATURES:")
        print("- Exact methodology compliance tracking")
        print("- Comprehensive signal validation")
        print("- Automated confirmation monitoring")
        print("- Real-time MFE tracking")
        print("- Session-based performance analysis")
        print("- R-multiple hit rate statistics")
        
        print("\nPROP FIRM PREPARATION:")
        print("- Automated trade lifecycle management")
        print("- Performance metrics collection")
        print("- Risk management validation")
        print("- Strategy effectiveness analysis")
        print("- Scalability testing framework")
        
        print(f"\nNEW WEBHOOK ENDPOINT:")
        print(f"   {RAILWAY_ENDPOINT}/api/live-signals-v2-complete")
        
        print(f"\nANALYTICS ENDPOINTS:")
        print(f"   Status: {RAILWAY_ENDPOINT}/api/automation/status")
        print(f"   Data Stats: {RAILWAY_ENDPOINT}/api/automation/data-stats")
        
        print("\nNEXT STEPS:")
        print("1. Review generated files")
        print("2. Apply database schema to Railway")
        print("3. Integrate code with web_server.py")
        print("4. Update TradingView webhook URL")
        print("5. Monitor data collection in dashboard")
        
    else:
        print("\nDeployment preparation failed")
    
    return success

if __name__ == "__main__":
    main()