"""
FULL AUTOMATION WEBHOOK HANDLERS
Handles all stages of the automated trading pipeline:
1. Signal Detection
2. Confirmation Detection  
3. Trade Activation
4. MFE Tracking
5. Trade Resolution

EXACT METHODOLOGY COMPLIANCE - NO FAKE DATA
"""

import json
import logging
from datetime import datetime
from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database connection
def get_db_connection():
    """Get database connection with error handling"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            raise Exception("DATABASE_URL environment variable not set")
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

# ============================================================================
# STAGE 1: SIGNAL DETECTION WEBHOOK
# ============================================================================

def handle_signal_detection():
    """
    Handles initial signal detection from TradingView
    Stores signal data and sets up confirmation monitoring
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ['signal_id', 'signal_type', 'timestamp', 'session', 'signal_candle']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate session (reject invalid sessions)
        if data['session'] == 'INVALID':
            return jsonify({"error": "Signal rejected - invalid trading session"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Insert signal into pending_signals table
            insert_query = """
            INSERT INTO pending_signals (
                signal_id, signal_type, timestamp, session,
                signal_open, signal_high, signal_low, signal_close, signal_volume,
                previous_open, previous_high, previous_low, previous_close,
                atr, volatility, signal_strength, bias, htf_status, 
                fvg_signal_type, htf_aligned, requires_confirmation,
                stop_loss_buffer, automation_stage, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            """
            
            signal_candle = data['signal_candle']
            previous_candle = data.get('previous_candle', {})
            market_context = data.get('market_context', {})
            fvg_data = data.get('fvg_data', {})
            methodology_data = data.get('methodology_data', {})
            
            cursor.execute(insert_query, (
                data['signal_id'],
                data['signal_type'],
                data['timestamp'],
                data['session'],
                signal_candle.get('open'),
                signal_candle.get('high'),
                signal_candle.get('low'),
                signal_candle.get('close'),
                signal_candle.get('volume'),
                previous_candle.get('open'),
                previous_candle.get('high'),
                previous_candle.get('low'),
                previous_candle.get('close'),
                market_context.get('atr'),
                market_context.get('volatility'),
                market_context.get('signal_strength'),
                fvg_data.get('bias'),
                fvg_data.get('htf_status'),
                fvg_data.get('signal_type'),
                fvg_data.get('htf_aligned'),
                methodology_data.get('requires_confirmation', True),
                methodology_data.get('stop_loss_buffer', 25),
                'SIGNAL_DETECTED'
            ))
            
            conn.commit()
            
            logging.info(f"Signal detected and stored: {data['signal_id']} - {data['signal_type']}")
            
            return jsonify({
                "status": "success",
                "message": "Signal detected and stored for confirmation monitoring",
                "signal_id": data['signal_id'],
                "automation_stage": "SIGNAL_DETECTED"
            }), 200
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error storing signal: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Signal detection error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# STAGE 2: CONFIRMATION DETECTION WEBHOOK
# ============================================================================

def handle_confirmation_detection():
    """
    Handles confirmation detection from TradingView
    Updates signal status and prepares for trade activation
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ['signal_id', 'confirmation_type', 'timestamp', 'entry_price', 'stop_loss_price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Update pending signal to confirmed status
            update_query = """
            UPDATE pending_signals 
            SET automation_stage = 'CONFIRMATION_DETECTED',
                confirmation_timestamp = %s,
                confirmation_open = %s,
                confirmation_high = %s,
                confirmation_low = %s,
                confirmation_close = %s,
                calculated_entry_price = %s,
                calculated_stop_loss = %s,
                risk_distance = %s,
                updated_at = NOW()
            WHERE signal_id = %s AND automation_stage = 'SIGNAL_DETECTED'
            """
            
            confirmation_candle = data.get('confirmation_candle', {})
            risk_distance = abs(float(data['entry_price']) - float(data['stop_loss_price']))
            
            cursor.execute(update_query, (
                data['timestamp'],
                confirmation_candle.get('open'),
                confirmation_candle.get('high'),
                confirmation_candle.get('low'),
                confirmation_candle.get('close'),
                data['entry_price'],
                data['stop_loss_price'],
                risk_distance,
                data['signal_id']
            ))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Signal not found or already processed"}), 404
            
            conn.commit()
            
            logging.info(f"Confirmation detected: {data['signal_id']} - Entry: {data['entry_price']}, SL: {data['stop_loss_price']}")
            
            return jsonify({
                "status": "success",
                "message": "Confirmation detected and trade prepared for activation",
                "signal_id": data['signal_id'],
                "automation_stage": "CONFIRMATION_DETECTED",
                "entry_price": data['entry_price'],
                "stop_loss_price": data['stop_loss_price'],
                "risk_distance": risk_distance
            }), 200
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error processing confirmation: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Confirmation detection error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# STAGE 3: TRADE ACTIVATION WEBHOOK
# ============================================================================

def handle_trade_activation():
    """
    Handles trade activation from TradingView
    Creates active trade entry in Signal Lab V2
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ['trade_id', 'trade_type', 'timestamp', 'actual_entry_price', 'stop_loss_price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Get original signal data
            signal_query = """
            SELECT * FROM pending_signals 
            WHERE signal_id = %s AND automation_stage = 'CONFIRMATION_DETECTED'
            """
            cursor.execute(signal_query, (data['trade_id'],))
            signal_data = cursor.fetchone()
            
            if not signal_data:
                return jsonify({"error": "Confirmed signal not found"}), 404
            
            # Create active trade in Signal Lab V2
            trade_insert = """
            INSERT INTO signal_lab_v2_trades (
                trade_id, signal_type, timestamp, session,
                signal_price, entry_price, stop_loss_price, risk_distance,
                current_mfe, max_mfe, trade_status, automation_source,
                signal_strength, htf_aligned, fvg_signal_type,
                atr, volatility, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            """
            
            entry_candle = data.get('entry_candle', {})
            risk_distance = abs(float(data['actual_entry_price']) - float(data['stop_loss_price']))
            initial_mfe = float(data.get('initial_mfe', 0.0))
            
            cursor.execute(trade_insert, (
                data['trade_id'],
                data['trade_type'],
                data['timestamp'],
                data.get('session', signal_data['session']),
                signal_data['signal_close'],  # Use signal candle close as signal price
                data['actual_entry_price'],
                data['stop_loss_price'],
                risk_distance,
                initial_mfe,
                initial_mfe,
                'ACTIVE',
                'FULL_AUTOMATION',
                signal_data['signal_strength'],
                signal_data['htf_aligned'],
                signal_data['fvg_signal_type'],
                signal_data['atr'],
                signal_data['volatility']
            ))
            
            # Update pending signal to activated
            update_query = """
            UPDATE pending_signals 
            SET automation_stage = 'TRADE_ACTIVATED',
                actual_entry_price = %s,
                actual_entry_timestamp = %s,
                initial_mfe = %s,
                updated_at = NOW()
            WHERE signal_id = %s
            """
            
            cursor.execute(update_query, (
                data['actual_entry_price'],
                data['timestamp'],
                initial_mfe,
                data['trade_id']
            ))
            
            conn.commit()
            
            logging.info(f"Trade activated: {data['trade_id']} - {data['trade_type']} at {data['actual_entry_price']}")
            
            return jsonify({
                "status": "success",
                "message": "Trade activated and added to Signal Lab V2",
                "trade_id": data['trade_id'],
                "automation_stage": "TRADE_ACTIVATED",
                "actual_entry_price": data['actual_entry_price'],
                "stop_loss_price": data['stop_loss_price'],
                "initial_mfe": initial_mfe
            }), 200
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error activating trade: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Trade activation error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# STAGE 4: MFE UPDATE WEBHOOK
# ============================================================================

def handle_mfe_update():
    """
    Handles MFE updates from TradingView
    Updates maximum favorable excursion for active trades
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ['trade_id', 'timestamp', 'current_mfe']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Update MFE for active trade
            update_query = """
            UPDATE signal_lab_v2_trades 
            SET current_mfe = %s,
                max_mfe = GREATEST(max_mfe, %s),
                last_mfe_update = %s,
                updated_at = NOW()
            WHERE trade_id = %s AND trade_status = 'ACTIVE'
            """
            
            current_mfe = float(data['current_mfe'])
            
            cursor.execute(update_query, (
                current_mfe,
                current_mfe,
                data['timestamp'],
                data['trade_id']
            ))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Active trade not found"}), 404
            
            conn.commit()
            
            logging.info(f"MFE updated: {data['trade_id']} - Current MFE: {current_mfe}R")
            
            return jsonify({
                "status": "success",
                "message": "MFE updated successfully",
                "trade_id": data['trade_id'],
                "current_mfe": current_mfe,
                "automation_stage": "MFE_UPDATE"
            }), 200
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error updating MFE: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"MFE update error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# STAGE 5: TRADE RESOLUTION WEBHOOK
# ============================================================================

def handle_trade_resolution():
    """
    Handles trade resolution from TradingView
    Finalizes trade with stop loss or break even outcome
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ['trade_id', 'resolution_type', 'timestamp', 'final_mfe']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Update trade to resolved status
            resolution_type = data['resolution_type']  # 'STOP_LOSS' or 'BREAK_EVEN'
            final_mfe = float(data['final_mfe'])
            
            # Calculate outcome based on resolution type
            if resolution_type == 'STOP_LOSS':
                outcome = -1.0  # -1R loss
                trade_status = 'STOPPED_OUT'
            elif resolution_type == 'BREAK_EVEN':
                outcome = 0.0   # 0R break even
                trade_status = 'BREAK_EVEN'
            else:
                return jsonify({"error": f"Invalid resolution type: {resolution_type}"}), 400
            
            update_query = """
            UPDATE signal_lab_v2_trades 
            SET trade_status = %s,
                final_mfe = %s,
                outcome_r = %s,
                resolution_type = %s,
                resolution_timestamp = %s,
                resolution_price = %s,
                resolved_at = NOW(),
                updated_at = NOW()
            WHERE trade_id = %s AND trade_status = 'ACTIVE'
            """
            
            cursor.execute(update_query, (
                trade_status,
                final_mfe,
                outcome,
                resolution_type,
                data['timestamp'],
                data.get('resolution_price'),
                data['trade_id']
            ))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Active trade not found"}), 404
            
            # Update pending signal to resolved
            signal_update = """
            UPDATE pending_signals 
            SET automation_stage = 'TRADE_RESOLVED',
                final_outcome = %s,
                final_mfe = %s,
                resolution_timestamp = %s,
                updated_at = NOW()
            WHERE signal_id = %s
            """
            
            cursor.execute(signal_update, (
                outcome,
                final_mfe,
                data['timestamp'],
                data['trade_id']
            ))
            
            conn.commit()
            
            logging.info(f"Trade resolved: {data['trade_id']} - {resolution_type} - Final MFE: {final_mfe}R")
            
            return jsonify({
                "status": "success",
                "message": f"Trade resolved: {resolution_type}",
                "trade_id": data['trade_id'],
                "resolution_type": resolution_type,
                "final_mfe": final_mfe,
                "outcome_r": outcome,
                "automation_stage": "TRADE_RESOLVED"
            }), 200
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error resolving trade: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Trade resolution error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# SIGNAL CANCELLATION WEBHOOK
# ============================================================================

def handle_signal_cancellation():
    """
    Handles signal cancellation from TradingView
    Cancels pending signals due to opposing signals
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ['signal_id', 'cancellation_reason', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Update pending signal to cancelled
            update_query = """
            UPDATE pending_signals 
            SET automation_stage = 'SIGNAL_CANCELLED',
                cancellation_reason = %s,
                cancellation_timestamp = %s,
                updated_at = NOW()
            WHERE signal_id = %s AND automation_stage = 'SIGNAL_DETECTED'
            """
            
            cursor.execute(update_query, (
                data['cancellation_reason'],
                data['timestamp'],
                data['signal_id']
            ))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Pending signal not found"}), 404
            
            conn.commit()
            
            logging.info(f"Signal cancelled: {data['signal_id']} - Reason: {data['cancellation_reason']}")
            
            return jsonify({
                "status": "success",
                "message": "Signal cancelled successfully",
                "signal_id": data['signal_id'],
                "cancellation_reason": data['cancellation_reason'],
                "automation_stage": "SIGNAL_CANCELLED"
            }), 200
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error cancelling signal: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Signal cancellation error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# AUTOMATION STATUS ENDPOINTS
# ============================================================================

def get_automation_status():
    """Get current automation status and statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = conn.cursor()
            
            # Get automation statistics
            stats_query = """
            SELECT 
                automation_stage,
                COUNT(*) as count,
                MAX(created_at) as latest_update
            FROM pending_signals 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY automation_stage
            ORDER BY automation_stage
            """
            
            cursor.execute(stats_query)
            stage_stats = cursor.fetchall()
            
            # Get active trades count
            active_query = """
            SELECT COUNT(*) as active_trades
            FROM signal_lab_v2_trades 
            WHERE trade_status = 'ACTIVE'
            """
            
            cursor.execute(active_query)
            active_result = cursor.fetchone()
            active_trades = active_result['active_trades'] if active_result else 0
            
            # Get recent automation activity
            recent_query = """
            SELECT signal_id, signal_type, automation_stage, created_at, updated_at
            FROM pending_signals 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC
            LIMIT 10
            """
            
            cursor.execute(recent_query)
            recent_activity = cursor.fetchall()
            
            return jsonify({
                "status": "success",
                "automation_enabled": True,
                "active_trades": active_trades,
                "stage_statistics": [dict(row) for row in stage_stats],
                "recent_activity": [dict(row) for row in recent_activity],
                "last_updated": datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting automation status: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Automation status error: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# ============================================================================
# WEBHOOK ROUTE MAPPINGS FOR FLASK APP
# ============================================================================

def register_automation_routes(app):
    """Register all automation webhook routes with Flask app"""
    
    # Stage 1: Signal Detection
    @app.route('/api/live-signals-v2', methods=['POST'])
    def signal_detection_webhook():
        return handle_signal_detection()
    
    # Stage 2: Confirmation Detection
    @app.route('/api/confirmations', methods=['POST'])
    def confirmation_webhook():
        return handle_confirmation_detection()
    
    # Stage 3: Trade Activation
    @app.route('/api/trade-activation', methods=['POST'])
    def trade_activation_webhook():
        return handle_trade_activation()
    
    # Stage 4: MFE Updates
    @app.route('/api/mfe-updates', methods=['POST'])
    def mfe_update_webhook():
        return handle_mfe_update()
    
    # Stage 5: Trade Resolution
    @app.route('/api/trade-resolution', methods=['POST'])
    def trade_resolution_webhook():
        return handle_trade_resolution()
    
    # Signal Cancellation
    @app.route('/api/signal-cancellation', methods=['POST'])
    def signal_cancellation_webhook():
        return handle_signal_cancellation()
    
    # Automation Status
    @app.route('/api/automation-status', methods=['GET'])
    def automation_status_endpoint():
        return get_automation_status()
    
    logging.info("Full automation webhook routes registered successfully")