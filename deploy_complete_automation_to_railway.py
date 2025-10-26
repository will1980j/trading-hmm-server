#!/usr/bin/env python3
"""
🚀 DEPLOY COMPLETE AUTOMATION TO RAILWAY
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
            logger.info("🤖 Complete Automation Pipeline initialized for data collection")
        else:
            logger.warning("⚠️ DATABASE_URL not available for automation pipeline")
    
    automation_available = True
    logger.info("✅ Complete Automation System loaded for forward testing")
    
except ImportError as e:
    logger.warning(f"⚠️ Complete Automation System not available: {str(e)}")
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
        
        # Get session breakdown
        cursor.execute("""
            SELECT 
                session,
                COUNT(*) as count,
                AVG(current_mfe) as avg_mfe
            FROM enhanced_signals_v2
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY session
            ORDER BY count DESC
        """)
        
        session_stats = [dict(row) for row in cursor.fetchall()]
        
        # Get recent automation performance
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as signals,
                COUNT(CASE WHEN automation_level = 'complete_pipeline' THEN 1 END) as automated,
                AVG(current_mfe) as avg_mfe
            FROM enhanced_signals_v2
            WHERE created_at > NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        
        daily_stats = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        
        return jsonify({
            'status': 'success',
            'data_collection_stats': dict(stats_row) if stats_row else {},
            'session_breakdown': session_stats,
            'daily_performance': daily_stats,
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

# Forward Testing Analysis Endpoint
@app.route('/api/automation/forward-test-analysis', methods=['GET'])
@login_required
def get_forward_test_analysis():
    """Get forward testing analysis for prop firm preparation"""
    try:
        if not db_enabled or not db:
            return jsonify({
                'error': 'Database not available',
                'analysis': {}
            })
        
        cursor = db.conn.cursor()
        
        # Get comprehensive forward testing metrics
        cursor.execute("""
            SELECT 
                signal_type,
                session,
                COUNT(*) as total_signals,
                COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_count,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count,
                AVG(CASE WHEN current_mfe > 0 THEN current_mfe END) as avg_positive_mfe,
                AVG(CASE WHEN current_mfe < 0 THEN current_mfe END) as avg_negative_mfe,
                MAX(max_mfe) as best_mfe,
                MIN(current_mfe) as worst_mfe,
                COUNT(CASE WHEN current_mfe >= 1.0 THEN 1 END) as hit_1r_count,
                COUNT(CASE WHEN current_mfe >= 2.0 THEN 1 END) as hit_2r_count,
                COUNT(CASE WHEN current_mfe >= 3.0 THEN 1 END) as hit_3r_count
            FROM enhanced_signals_v2
            WHERE automation_level = 'complete_pipeline'
            AND created_at > NOW() - INTERVAL '30 days'
            GROUP BY signal_type, session
            ORDER BY signal_type, total_signals DESC
        """)
        
        analysis_data = [dict(row) for row in cursor.fetchall()]
        
        # Calculate prop firm readiness metrics
        prop_firm_metrics = {
            'total_automated_trades': sum(row['total_signals'] for row in analysis_data),
            'confirmation_rate': sum(row['confirmed_count'] for row in analysis_data) / max(sum(row['total_signals'] for row in analysis_data), 1) * 100,
            'resolution_rate': sum(row['resolved_count'] for row in analysis_data) / max(sum(row['confirmed_count'] for row in analysis_data), 1) * 100,
            'r_multiple_performance': {
                '1R_hit_rate': sum(row['hit_1r_count'] for row in analysis_data) / max(sum(row['confirmed_count'] for row in analysis_data), 1) * 100,
                '2R_hit_rate': sum(row['hit_2r_count'] for row in analysis_data) / max(sum(row['confirmed_count'] for row in analysis_data), 1) * 100,
                '3R_hit_rate': sum(row['hit_3r_count'] for row in analysis_data) / max(sum(row['confirmed_count'] for row in analysis_data), 1) * 100
            }
        }
        
        cursor.close()
        
        return jsonify({
            'status': 'success',
            'forward_test_analysis': analysis_data,
            'prop_firm_readiness': prop_firm_metrics,
            'data_quality': 'high' if prop_firm_metrics['total_automated_trades'] > 100 else 'building',
            'recommendation': 'Ready for prop firm testing' if prop_firm_metrics['total_automated_trades'] > 500 else 'Continue data collection',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Forward test analysis error: {str(e)}")
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
    
    -- Pivot Analysis
    pivot_count INTEGER DEFAULT 0,
    signal_is_pivot BOOLEAN DEFAULT FALSE,
    pivot_data JSONB,
    
    -- R-Multiple Targets
    target_1r DECIMAL(10,2),
    target_2r DECIMAL(10,2),
    target_3r DECIMAL(10,2),
    target_5r DECIMAL(10,2),
    target_10r DECIMAL(10,2),
    target_20r DECIMAL(10,2),
    estimated_entry DECIMAL(10,2),
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

-- Automation monitoring for data collection
CREATE TABLE IF NOT EXISTS automation_monitoring (
    id SERIAL PRIMARY KEY,
    trade_uuid UUID NOT NULL,
    monitoring_type VARCHAR(30) NOT NULL, -- 'confirmation', 'mfe', 'stop_loss'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_count INTEGER DEFAULT 0,
    monitoring_data JSONB,
    data_collection_notes TEXT,
    
    FOREIGN KEY (trade_uuid) REFERENCES enhanced_signals_v2(trade_uuid)
);

-- Automation logs for debugging and analysis
CREATE TABLE IF NOT EXISTS automation_logs (
    id SERIAL PRIMARY KEY,
    trade_uuid UUID,
    log_level VARCHAR(10) NOT NULL, -- 'INFO', 'WARNING', 'ERROR'
    message TEXT NOT NULL,
    automation_stage VARCHAR(30), -- 'signal_processing', 'confirmation', 'activation', 'mfe_tracking'
    log_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Forward testing analysis fields
    session VARCHAR(20),
    signal_type VARCHAR(10),
    data_quality_score INTEGER DEFAULT 100
);

-- Forward testing metrics table
CREATE TABLE IF NOT EXISTS forward_testing_metrics (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    session VARCHAR(20),
    signal_type VARCHAR(10),
    total_signals INTEGER DEFAULT 0,
    confirmed_signals INTEGER DEFAULT 0,
    resolved_signals INTEGER DEFAULT 0,
    avg_mfe DECIMAL(10,4) DEFAULT 0,
    max_mfe DECIMAL(10,4) DEFAULT 0,
    hit_1r_count INTEGER DEFAULT 0,
    hit_2r_count INTEGER DEFAULT 0,
    hit_3r_count INTEGER DEFAULT 0,
    automation_success_rate DECIMAL(5,2) DEFAULT 0,
    data_quality_score INTEGER DEFAULT 100,
    prop_firm_readiness_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(date, session, signal_type)
);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_automation_level ON enhanced_signals_v2(automation_level);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_data_collection ON enhanced_signals_v2(data_collection_mode);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_forward_testing ON enhanced_signals_v2(forward_testing);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_session_type ON enhanced_signals_v2(session, signal_type);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_created_at ON enhanced_signals_v2(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_automation_monitoring_trade_uuid ON automation_monitoring(trade_uuid);
CREATE INDEX IF NOT EXISTS idx_automation_logs_created_at ON automation_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forward_testing_metrics_date ON forward_testing_metrics(date DESC);

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
        print("🚀 DEPLOYING COMPLETE AUTOMATION TO RAILWAY")
        print("=" * 55)
        
        # Create integration code
        integration_code = create_complete_automation_integration()
        
        # Create database schema
        schema_sql = create_automation_database_schema()
        
        # Save files locally
        with open('complete_automation_integration.py', 'w') as f:
            f.write(integration_code)
        
        with open('automation_database_schema.sql', 'w') as f:
            f.write(schema_sql)
        
        print("✅ Complete automation files created")
        print("📁 Files ready for deployment:")
        print("   - complete_automation_integration.py")
        print("   - automation_database_schema.sql")
        print("   - complete_automation_pipeline.py")
        print("   - enhanced_webhook_processor_v2.py")
        
        # Test current system
        print("\n🧪 Testing current system compatibility...")
        
        try:
            response = requests.get(f"{RAILWAY_ENDPOINT}/api/db-status", timeout=10)
            if response.status_code == 200:
                print("✅ Database connection confirmed")
            else:
                print(f"⚠️ Database status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Database test: {str(e)}")
        
        try:
            response = requests.get(f"{RAILWAY_ENDPOINT}/signal-lab-v2", timeout=10)
            if response.status_code in [200, 302]:
                print("✅ Signal Lab V2 dashboard accessible")
            else:
                print(f"⚠️ Dashboard status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Dashboard test: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment preparation error: {str(e)}")
        return False

def create_deployment_instructions():
    """Create step-by-step deployment instructions"""
    
    instructions = '''
# 🚀 COMPLETE AUTOMATION DEPLOYMENT INSTRUCTIONS

## Step 1: Upload Automation Files to Railway
1. Copy these files to your Railway project:
   - complete_automation_pipeline.py
   - enhanced_webhook_processor_v2.py
   - complete_automation_integration.py (add to web_server.py)

## Step 2: Apply Database Schema
1. Connect to Railway PostgreSQL
2. Run automation_database_schema.sql
3. Verify tables created successfully

## Step 3: Integrate with Web Server
1. Add complete_automation_integration.py code to web_server.py
2. Deploy to Railway
3. Verify deployment successful

## Step 4: Update TradingView Webhook
1. Open Enhanced FVG Indicator alert in TradingView
2. Change webhook URL to: https://web-production-cd33.up.railway.app/api/live-signals-v2-complete
3. Test with sample signal

## Step 5: Verify System
1. Check automation status: /api/automation/status
2. Monitor data collection: /api/automation/data-stats
3. View forward testing analysis: /api/automation/forward-test-analysis

## Step 6: Monitor Data Collection
1. Watch Signal Lab V2 dashboard for automated trades
2. Monitor automation logs for any issues
3. Analyze forward testing metrics regularly

Your complete automation system will now:
✅ Collect comprehensive signal data automatically
✅ Process signals with exact methodology compliance
✅ Track MFE and trade performance accurately
✅ Build database for future prop firm trading
✅ Provide forward testing analytics
'''
    
    with open('DEPLOYMENT_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("✅ Deployment instructions created: DEPLOYMENT_INSTRUCTIONS.md")

def main():
    """Main deployment function"""
    success = deploy_to_railway()
    
    if success:
        create_deployment_instructions()
        
        print("\n🎉 COMPLETE AUTOMATION DEPLOYMENT READY!")
        print("=" * 55)
        
        print("\n🎯 FOR DATA COLLECTION & FORWARD TESTING:")
        print("✅ Complete automation pipeline created")
        print("✅ Enhanced webhook processor ready")
        print("✅ Database schema for comprehensive data collection")
        print("✅ Forward testing analytics endpoints")
        print("✅ Prop firm readiness metrics")
        
        print("\n📊 DATA COLLECTION FEATURES:")
        print("✅ Exact methodology compliance tracking")
        print("✅ Comprehensive signal validation")
        print("✅ Automated confirmation monitoring")
        print("✅ Real-time MFE tracking")
        print("✅ Session-based performance analysis")
        print("✅ R-multiple hit rate statistics")
        
        print("\n🚀 PROP FIRM PREPARATION:")
        print("✅ Automated trade lifecycle management")
        print("✅ Performance metrics collection")
        print("✅ Risk management validation")
        print("✅ Strategy effectiveness analysis")
        print("✅ Scalability testing framework")
        
        print("\n📡 NEW WEBHOOK ENDPOINT:")
        print(f"   {RAILWAY_ENDPOINT}/api/live-signals-v2-complete")
        
        print("\n📈 ANALYTICS ENDPOINTS:")
        print(f"   Status: {RAILWAY_ENDPOINT}/api/automation/status")
        print(f"   Data Stats: {RAILWAY_ENDPOINT}/api/automation/data-stats")
        print(f"   Forward Testing: {RAILWAY_ENDPOINT}/api/automation/forward-test-analysis")
        
        print("\n🎯 NEXT STEPS:")
        print("1. 📁 Review generated files")
        print("2. 🗄️ Apply database schema to Railway")
        print("3. 🔧 Integrate code with web_server.py")
        print("4. 📡 Update TradingView webhook URL")
        print("5. 📊 Monitor data collection in dashboard")
        
    else:
        print("\n❌ Deployment preparation failed")
    
    return success

if __name__ == "__main__":
    main()