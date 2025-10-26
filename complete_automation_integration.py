
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
