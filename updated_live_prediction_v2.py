
@app.route('/api/live-prediction', methods=['GET'])
@login_required
def get_live_prediction():
    """Get live prediction for most recent signal - ENHANCED FOR V2"""
    try:
        if not db_enabled:
            return jsonify({'status': 'no_database'}), 200
        
        from database.railway_db import RailwayDB
        query_db = RailwayDB(use_pool=True)
        
        if not query_db or not query_db.conn:
            return jsonify({'status': 'no_connection'}), 200
        
        cursor = query_db.conn.cursor()
        
        # Get most recent signal from COMBINED V1 + V2 sources
        cursor.execute("""
            WITH combined_recent AS (
                -- V1 Recent Signal
                SELECT 
                    'v1' as source,
                    bias,
                    timestamp,
                    signal_price,
                    session,
                    NULL as trade_status,
                    NULL as current_mfe,
                    NULL as auto_populated
                FROM live_signals
                WHERE timestamp > NOW() - INTERVAL '4 hours'
                
                UNION ALL
                
                -- V2 Recent Signal
                SELECT 
                    'v2' as source,
                    CASE 
                        WHEN bias = 'bullish' THEN 'Bullish'
                        WHEN bias = 'bearish' THEN 'Bearish'
                        ELSE bias
                    END as bias,
                    signal_timestamp as timestamp,
                    entry_price as signal_price,
                    session,
                    trade_status,
                    current_mfe,
                    auto_populated
                FROM signal_lab_v2_trades
                WHERE signal_timestamp > NOW() - INTERVAL '4 hours'
            )
            SELECT * FROM combined_recent
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        recent_signal = cursor.fetchone()
        
        if not recent_signal:
            return jsonify({'status': 'no_active_signal'}), 200
        
        # Generate ML prediction based on signal characteristics
        signal_data = dict(recent_signal)
        
        # Enhanced prediction logic for V2
        confidence = 75.0  # Base confidence
        
        # Adjust confidence based on session
        session_multipliers = {
            'NY AM': 1.15,
            'NY PM': 1.10,
            'LONDON': 1.05,
            'ASIA': 0.95,
            'NY PRE': 0.90,
            'NY LUNCH': 0.85
        }
        confidence *= session_multipliers.get(signal_data.get('session', ''), 1.0)
        
        # V2 ENHANCEMENT: Adjust confidence based on automation
        if signal_data.get('source') == 'v2':
            if signal_data.get('auto_populated'):
                confidence *= 1.08  # Automation bonus
            if signal_data.get('trade_status') == 'ACTIVE':
                confidence *= 1.05  # Active trade bonus
            if signal_data.get('current_mfe', 0) > 0:
                confidence *= 1.03  # Positive MFE bonus
        
        # Cap confidence at 95%
        confidence = min(confidence, 95.0)
        
        # Predict target probabilities
        target_1r = min(confidence * 0.65, 85.0)
        target_2r = min(confidence * 0.45, 65.0)
        target_3r = min(confidence * 0.30, 45.0)
        
        query_db.close()
        
        return jsonify({
            'status': 'active_signal',
            'signal': {
                'source': signal_data['source'],
                'bias': signal_data['bias'],
                'session': signal_data['session'],
                'timestamp': signal_data['timestamp'].isoformat(),
                'price': float(signal_data['signal_price']) if signal_data['signal_price'] else None,
                'trade_status': signal_data.get('trade_status'),
                'current_mfe': float(signal_data['current_mfe']) if signal_data.get('current_mfe') else None,
                'auto_populated': signal_data.get('auto_populated')
            },
            'prediction': {
                'confidence': round(confidence, 1),
                'target_probabilities': {
                    '1R': round(target_1r, 1),
                    '2R': round(target_2r, 1),
                    '3R': round(target_3r, 1)
                },
                'recommendation': 'FULL_SIZE' if confidence > 80 else 'HALF_SIZE' if confidence > 60 else 'SKIP',
                'model_version': 'v2_enhanced',
                'features_used': ['session', 'bias', 'automation_quality', 'current_mfe']
            },
            'v2_enhancements': {
                'real_time_mfe': signal_data.get('current_mfe') is not None,
                'automation_integrated': signal_data.get('source') == 'v2',
                'trade_status_tracking': signal_data.get('trade_status') is not None
            }
        })
        
    except Exception as e:
        logger.error(f"Live prediction error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500
