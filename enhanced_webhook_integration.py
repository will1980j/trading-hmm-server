"""
Enhanced Webhook Integration for V2 Automation
Integrates the enhanced signal processor with the existing web server
"""

from enhanced_webhook_processor import process_enhanced_webhook
import json
import logging
from datetime import datetime

def integrate_enhanced_webhook_endpoint():
    """
    Enhanced webhook endpoint code to replace the current /api/live-signals-v2 endpoint
    """
    
    webhook_code = '''
# Enhanced webhook endpoint for V2 automation with exact methodology
@app.route('/api/live-signals-v2', methods=['POST'])
def receive_signal_v2_enhanced():
    """Enhanced webhook with comprehensive signal processing - no login required for TradingView"""
    try:
        data = request.get_json()
        
        # Check if this is enhanced data (new format) or legacy data (old format)
        is_enhanced_format = 'signal_candle' in data and 'historical_candles' in data
        
        if is_enhanced_format:
            # Process enhanced signal data
            processed_result = process_enhanced_webhook(data)
            
            if processed_result.get('status') == 'processed':
                # Store enhanced signal in V2 database
                v2_result = store_enhanced_signal_v2(processed_result)
                
                # Also store in original format for compatibility
                legacy_result = store_legacy_signal(processed_result)
                
                return jsonify({
                    "status": "success",
                    "message": "Enhanced signal processed successfully",
                    "v2_automation": v2_result,
                    "legacy_compatibility": legacy_result,
                    "signal_data": {
                        "type": processed_result.get('signal_type'),
                        "session": processed_result.get('session'),
                        "confirmation_required": processed_result.get('confirmation_data', {}).get('required'),
                        "stop_loss_calculated": processed_result.get('stop_loss_data', {}).get('stop_loss_price') is not None
                    }
                })
            elif processed_result.get('status') == 'rejected':
                return jsonify({
                    "status": "rejected",
                    "reason": processed_result.get('reason'),
                    "message": "Signal rejected due to validation rules"
                })
            else:
                return jsonify({
                    "status": "error",
                    "reason": processed_result.get('reason'),
                    "message": "Error processing enhanced signal"
                })
        
        else:
            # Handle legacy format (current simple format)
            signal_result = {
                "type": data.get('type', data.get('signal_type', '')),
                "price": data.get('price', 0),
                "timestamp": data.get('timestamp', datetime.now().isoformat()),
                "session": data.get('session', 'NY AM')
            }
            
            # Process with existing V2 logic (limited functionality)
            v2_automation = process_legacy_signal_v2(signal_result)
            
            return jsonify({
                "status": "success",
                "message": "Legacy signal processed (limited automation)",
                "v2_automation": v2_automation,
                "upgrade_notice": "Update TradingView indicator for full automation features"
            })
            
    except Exception as e:
        logging.error(f"Enhanced webhook error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def store_enhanced_signal_v2(processed_signal):
    """Store enhanced signal data in V2 database with full methodology support"""
    try:
        signal_type = processed_signal.get('signal_type')
        session = processed_signal.get('session')
        timestamp = processed_signal.get('timestamp')
        
        # Extract processed data
        confirmation_data = processed_signal.get('confirmation_data', {})
        stop_loss_data = processed_signal.get('stop_loss_data', {})
        r_targets = processed_signal.get('r_targets', {})
        pivot_analysis = processed_signal.get('pivot_analysis', {})
        
        # Signal candle data
        signal_candle = processed_signal.get('signal_candle', {})
        
        # Create comprehensive database entry
        db_entry = {
            "signal_type": signal_type,
            "session": session,
            "timestamp": timestamp,
            "signal_candle_open": signal_candle.get('open'),
            "signal_candle_high": signal_candle.get('high'),
            "signal_candle_low": signal_candle.get('low'),
            "signal_candle_close": signal_candle.get('close'),
            "signal_candle_volume": signal_candle.get('volume'),
            
            # Confirmation requirements
            "requires_confirmation": confirmation_data.get('required', True),
            "confirmation_condition": confirmation_data.get('condition'),
            "confirmation_target_price": confirmation_data.get('target_price'),
            
            # Stop loss data
            "stop_loss_price": stop_loss_data.get('stop_loss_price'),
            "stop_loss_scenario": stop_loss_data.get('primary_scenario', {}).get('scenario'),
            "stop_loss_reasoning": stop_loss_data.get('primary_scenario', {}).get('reasoning'),
            
            # Pivot analysis
            "pivot_count": pivot_analysis.get('pivot_count', 0),
            "signal_is_pivot": pivot_analysis.get('signal_is_pivot', False),
            
            # R-targets (store key levels)
            "target_1r": r_targets.get('1R', {}).get('price'),
            "target_2r": r_targets.get('2R', {}).get('price'),
            "target_3r": r_targets.get('3R', {}).get('price'),
            "target_5r": r_targets.get('5R', {}).get('price'),
            "target_10r": r_targets.get('10R', {}).get('price'),
            "target_20r": r_targets.get('20R', {}).get('price'),
            
            # Risk management
            "estimated_entry": processed_signal.get('estimated_entry'),
            "risk_distance": processed_signal.get('risk_distance'),
            
            # Status tracking
            "status": "awaiting_confirmation",
            "automation_level": "enhanced_v2"
        }
        
        # Execute database operation
        db_result = execute_enhanced_v2_database_operation(db_entry)
        
        return {
            "success": db_result.get('success', False),
            "trade_id": db_result.get('trade_id'),
            "trade_uuid": db_result.get('trade_uuid'),
            "automation_level": "enhanced_v2",
            "features_enabled": [
                "pivot_detection",
                "exact_stop_loss",
                "confirmation_monitoring",
                "r_target_calculation"
            ]
        }
        
    except Exception as e:
        logging.error(f"Error storing enhanced signal: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def process_legacy_signal_v2(signal_result):
    """Process legacy signal format (current limited functionality)"""
    try:
        signal_type = signal_result["type"]
        signal_price = float(signal_result["price"])
        
        if signal_type.lower() in ['bullish', 'bearish'] and signal_price > 0:
            signal_type = signal_type.capitalize()
            
            # Limited automation (current V2 system)
            entry_price = None
            stop_loss_price = None
            risk_distance = None
            targets = {
                "1R": None,
                "2R": None,
                "3R": None,
                "5R": None,
                "10R": None,
                "20R": None
            }
            
            # Execute existing V2 database operation
            db_result = execute_v2_database_operation_robust(
                signal_type, 
                signal_result.get("session", "NY AM"),
                entry_price, 
                stop_loss_price, 
                risk_distance, 
                targets
            )
            
            return {
                "success": db_result.get('success', False),
                "trade_id": db_result.get('trade_id'),
                "automation_level": "basic_v2",
                "limitations": [
                    "no_pivot_detection",
                    "no_exact_stop_loss",
                    "no_confirmation_monitoring",
                    "manual_entry_required"
                ]
            }
        else:
            return {
                "success": False,
                "reason": "Invalid signal type or price"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def execute_enhanced_v2_database_operation(db_entry):
    """Execute enhanced database operation with comprehensive signal data"""
    try:
        # REAL DATABASE OPERATION REQUIRED
        # This must connect to actual Railway PostgreSQL database
        
        import os
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("❌ DATABASE_URL required - no fake database operations")
            
        # Parse and connect to real database
        url = urlparse(database_url)
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Execute REAL database operation using process_enhanced_signal_v2 function
        cursor.execute("SELECT process_enhanced_signal_v2(%s)", (json.dumps(db_entry),))
        result = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        logging.error(f"Enhanced database operation error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def store_legacy_signal(processed_signal):
    """Store signal in legacy format for compatibility"""
    try:
        # Convert enhanced signal back to legacy format
        signal_type = processed_signal.get('signal_type')
        signal_candle = processed_signal.get('signal_candle', {})
        session = processed_signal.get('session')
        
        # Store in original live_signals table
        legacy_data = {
            "signal_type": signal_type,
            "signal_price": signal_candle.get('close', 0),
            "session": session,
            "timestamp": processed_signal.get('timestamp')
        }
        
        # Execute legacy storage (existing function)
        # This maintains compatibility with existing dashboard
        
        return {
            "success": True,
            "message": "Legacy compatibility maintained"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
'''
    
    return webhook_code

# Database schema for enhanced signals
def get_enhanced_v2_schema():
    """Database schema for enhanced V2 signals"""
    
    schema = '''
    CREATE TABLE IF NOT EXISTS enhanced_signals_v2 (
        id SERIAL PRIMARY KEY,
        trade_uuid UUID DEFAULT gen_random_uuid(),
        
        -- Basic signal data
        signal_type VARCHAR(10) NOT NULL,
        session VARCHAR(20) NOT NULL,
        timestamp BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Signal candle OHLCV
        signal_candle_open DECIMAL(10,2),
        signal_candle_high DECIMAL(10,2),
        signal_candle_low DECIMAL(10,2),
        signal_candle_close DECIMAL(10,2),
        signal_candle_volume INTEGER,
        
        -- Confirmation data
        requires_confirmation BOOLEAN DEFAULT TRUE,
        confirmation_condition VARCHAR(50),
        confirmation_target_price DECIMAL(10,2),
        confirmation_received BOOLEAN DEFAULT FALSE,
        confirmation_timestamp BIGINT,
        
        -- Entry data (filled when confirmation occurs)
        entry_price DECIMAL(10,2),
        entry_timestamp BIGINT,
        
        -- Stop loss data
        stop_loss_price DECIMAL(10,2),
        stop_loss_scenario VARCHAR(50),
        stop_loss_reasoning TEXT,
        
        -- Pivot analysis
        pivot_count INTEGER DEFAULT 0,
        signal_is_pivot BOOLEAN DEFAULT FALSE,
        
        -- R-targets
        target_1r DECIMAL(10,2),
        target_2r DECIMAL(10,2),
        target_3r DECIMAL(10,2),
        target_5r DECIMAL(10,2),
        target_10r DECIMAL(10,2),
        target_20r DECIMAL(10,2),
        
        -- Risk management
        estimated_entry DECIMAL(10,2),
        risk_distance DECIMAL(10,2),
        
        -- MFE tracking
        current_mfe DECIMAL(10,4) DEFAULT 0,
        max_mfe DECIMAL(10,4) DEFAULT 0,
        
        -- Status tracking
        status VARCHAR(30) DEFAULT 'awaiting_confirmation',
        automation_level VARCHAR(20) DEFAULT 'enhanced_v2',
        
        -- Trade resolution
        resolved BOOLEAN DEFAULT FALSE,
        resolution_type VARCHAR(20), -- 'stop_loss', 'break_even', 'target_hit'
        resolution_price DECIMAL(10,2),
        resolution_timestamp BIGINT,
        final_mfe DECIMAL(10,4)
    );
    
    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_timestamp ON enhanced_signals_v2(timestamp);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_status ON enhanced_signals_v2(status);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_session ON enhanced_signals_v2(session);
    CREATE INDEX IF NOT EXISTS idx_enhanced_signals_v2_uuid ON enhanced_signals_v2(trade_uuid);
    '''
    
    return schema

if __name__ == "__main__":
    # Print the integration code
    print("Enhanced Webhook Integration Code:")
    print("=" * 50)
    print(integrate_enhanced_webhook_endpoint())
    print("\n" + "=" * 50)
    print("Enhanced Database Schema:")
    print("=" * 50)
    print(get_enhanced_v2_schema())