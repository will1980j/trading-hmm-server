
# ============================================================================
# ENHANCED V2 DUAL INDICATOR PROCESSING FUNCTIONS
# ============================================================================

def process_enhanced_signal_data_v2(raw_data):
    """Process comprehensive signal data from Enhanced FVG Indicator V2"""
    try:
        logger.info(f"[V2 ENHANCED] Processing signal data: {raw_data}")
        
        # Extract signal components from Enhanced FVG Indicator
        signal_type = raw_data.get("signal_type", "Unknown")
        
        # Signal candle data (from TradingView indicator)
        signal_candle = raw_data.get("signal_candle", {})
        
        # FVG analysis data
        fvg_data = raw_data.get("fvg_data", {})
        
        # HTF bias information
        htf_data = raw_data.get("htf_data", {})
        
        # Session and timing
        session_data = raw_data.get("session_data", {})
        
        # Methodology requirements
        methodology_data = raw_data.get("methodology_data", {})
        
        # Market context
        market_context = raw_data.get("market_context", {})
        
        # Create comprehensive signal record
        processed_signal = {
            "signal_type": signal_type,
            "timestamp": datetime.now(),
            "signal_candle_open": signal_candle.get("open"),
            "signal_candle_high": signal_candle.get("high"),
            "signal_candle_low": signal_candle.get("low"),
            "signal_candle_close": signal_candle.get("close"),
            "signal_candle_volume": signal_candle.get("volume"),
            "fvg_bias": fvg_data.get("bias"),
            "fvg_strength": fvg_data.get("strength"),
            "htf_aligned": htf_data.get("aligned", False),
            "htf_bias_1h": htf_data.get("bias_1h"),
            "htf_bias_15m": htf_data.get("bias_15m"),
            "htf_bias_5m": htf_data.get("bias_5m"),
            "session": session_data.get("current_session"),
            "session_valid": session_data.get("valid", False),
            "requires_confirmation": methodology_data.get("requires_confirmation", True),
            "stop_loss_buffer": methodology_data.get("stop_loss_buffer", 25),
            "confirmation_condition": methodology_data.get("confirmation_condition"),
            "status": "awaiting_confirmation",
            "automation_level": "enhanced_v2",
            "market_context": market_context,
            "raw_data": json.dumps(raw_data)
        }
        
        logger.info(f"[V2 ENHANCED] Signal processed: {signal_type} at {signal_candle.get('close')}")
        return processed_signal
        
    except Exception as e:
        logger.error(f"[V2 ENHANCED PROCESSING ERROR] {str(e)}")
        return {"error": str(e), "raw_data": json.dumps(raw_data)}

def store_enhanced_v2_signal(signal_data):
    """Store enhanced V2 signal in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert into enhanced_signals_v2 table
        insert_query = """
        INSERT INTO enhanced_signals_v2 (
            signal_type, session, timestamp, signal_candle_open, signal_candle_high,
            signal_candle_low, signal_candle_close, signal_candle_volume,
            requires_confirmation, confirmation_condition, stop_loss_scenario,
            automation_level, status, market_context, raw_signal_data
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id, trade_uuid;
        """
        
        cursor.execute(insert_query, (
            signal_data["signal_type"],
            signal_data["session"],
            int(datetime.now().timestamp() * 1000),  # Convert to milliseconds
            signal_data["signal_candle_open"],
            signal_data["signal_candle_high"],
            signal_data["signal_candle_low"],
            signal_data["signal_candle_close"],
            signal_data["signal_candle_volume"],
            signal_data["requires_confirmation"],
            signal_data["confirmation_condition"],
            "pending_calculation",
            signal_data["automation_level"],
            signal_data["status"],
            json.dumps(signal_data["market_context"]),
            signal_data["raw_data"]
        ))
        
        result = cursor.fetchone()
        signal_id = result[0]
        trade_uuid = result[1]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"[V2 ENHANCED STORED] ID: {signal_id}, UUID: {trade_uuid}")
        return {"signal_id": signal_id, "trade_uuid": str(trade_uuid)}
        
    except Exception as e:
        logger.error(f"[V2 ENHANCED STORAGE ERROR] {str(e)}")
        return {"error": str(e)}

def process_realtime_price_v2(price_data):
    """Process real-time price data for V2 system"""
    try:
        logger.info(f"[V2 PRICE] Processing: {price_data.get('price')} at {price_data.get('timestamp')}")
        
        # Store price data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert price update
        cursor.execute("""
            INSERT INTO realtime_prices (symbol, price, timestamp, session, volume, price_change)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            price_data.get("symbol", "NQ"),
            price_data.get("price"),
            price_data.get("timestamp"),
            price_data.get("session"),
            price_data.get("volume", 0),
            price_data.get("change", 0)
        ))
        
        price_id = cursor.fetchone()[0]
        
        # Update MFE for active trades
        update_mfe_for_active_trades_v2(cursor, price_data)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "price_id": price_id,
            "price": price_data.get("price"),
            "mfe_updates": "processed"
        }
        
    except Exception as e:
        logger.error(f"[V2 PRICE ERROR] {str(e)}")
        return {"error": str(e)}

def update_mfe_for_active_trades_v2(cursor, price_data):
    """Update MFE for all active V2 trades"""
    try:
        current_price = float(price_data.get("price", 0))
        current_timestamp = price_data.get("timestamp")
        
        # Get active trades with entry prices
        cursor.execute("""
            SELECT trade_uuid, signal_type, entry_price, stop_loss_price, current_mfe, max_mfe
            FROM enhanced_signals_v2 
            WHERE confirmation_received = TRUE 
            AND resolved = FALSE 
            AND entry_price IS NOT NULL
        """)
        
        active_trades = cursor.fetchall()
        
        for trade in active_trades:
            trade_uuid, signal_type, entry_price, stop_loss, current_mfe, max_mfe = trade
            
            if entry_price and stop_loss:
                # Calculate new MFE
                if signal_type.lower() == "bullish":
                    risk_distance = entry_price - stop_loss
                    if risk_distance > 0:
                        new_mfe = (current_price - entry_price) / risk_distance
                else:
                    risk_distance = stop_loss - entry_price
                    if risk_distance > 0:
                        new_mfe = (entry_price - current_price) / risk_distance
                
                # Update if new MFE is higher
                if new_mfe > (current_mfe or 0):
                    cursor.execute("""
                        UPDATE enhanced_signals_v2 
                        SET current_mfe = %s, max_mfe = GREATEST(max_mfe, %s)
                        WHERE trade_uuid = %s
                    """, (new_mfe, new_mfe, trade_uuid))
                    
                    # Record MFE update
                    cursor.execute("""
                        INSERT INTO realtime_mfe_updates (trade_uuid, price, mfe_value, is_new_high, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (trade_uuid, current_price, new_mfe, True, current_timestamp))
        
        logger.info(f"[V2 MFE] Updated {len(active_trades)} active trades")
        
    except Exception as e:
        logger.error(f"[V2 MFE UPDATE ERROR] {str(e)}")

def get_db_connection():
    """Get database connection for V2 operations"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            raise Exception("DATABASE_URL environment variable not set")
        
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"V2 Database connection error: {str(e)}")
        raise

# ============================================================================
# ENHANCED V2 API ENDPOINTS
# ============================================================================

@app.route('/api/v2/signals/comprehensive', methods=['GET'])
@login_required
def get_comprehensive_v2_signals():
    """Get comprehensive V2 signals with all data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, trade_uuid, signal_type, session, timestamp,
                signal_candle_open, signal_candle_high, signal_candle_low, signal_candle_close,
                requires_confirmation, confirmation_received, confirmation_timestamp,
                entry_price, stop_loss_price, current_mfe, max_mfe,
                status, automation_level, resolved, resolution_type,
                market_context, raw_signal_data
            FROM enhanced_signals_v2 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'id': row['id'],
                'trade_uuid': str(row['trade_uuid']),
                'signal_type': row['signal_type'],
                'session': row['session'],
                'timestamp': row['timestamp'],
                'signal_candle': {
                    'open': float(row['signal_candle_open']) if row['signal_candle_open'] else None,
                    'high': float(row['signal_candle_high']) if row['signal_candle_high'] else None,
                    'low': float(row['signal_candle_low']) if row['signal_candle_low'] else None,
                    'close': float(row['signal_candle_close']) if row['signal_candle_close'] else None
                },
                'confirmation': {
                    'required': row['requires_confirmation'],
                    'received': row['confirmation_received'],
                    'timestamp': row['confirmation_timestamp']
                },
                'trade_data': {
                    'entry_price': float(row['entry_price']) if row['entry_price'] else None,
                    'stop_loss_price': float(row['stop_loss_price']) if row['stop_loss_price'] else None,
                    'current_mfe': float(row['current_mfe']) if row['current_mfe'] else 0,
                    'max_mfe': float(row['max_mfe']) if row['max_mfe'] else 0
                },
                'status': row['status'],
                'automation_level': row['automation_level'],
                'resolved': row['resolved'],
                'resolution_type': row['resolution_type'],
                'market_context': row['market_context'],
                'raw_data': row['raw_signal_data']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'count': len(signals),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Comprehensive V2 signals error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/v2/price/stream', methods=['GET'])
@login_required
def get_v2_price_stream():
    """Get recent price stream data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 100)
        
        cursor.execute("""
            SELECT symbol, price, timestamp, session, volume, price_change, created_at
            FROM realtime_prices 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        
        prices = []
        for row in cursor.fetchall():
            prices.append({
                'symbol': row['symbol'],
                'price': float(row['price']),
                'timestamp': row['timestamp'],
                'session': row['session'],
                'volume': row['volume'],
                'change': float(row['price_change']) if row['price_change'] else 0,
                'created_at': row['created_at'].isoformat()
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'prices': prices,
            'count': len(prices)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/v2/mfe/updates', methods=['GET'])
@login_required
def get_v2_mfe_updates():
    """Get recent MFE updates for active trades"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        trade_uuid = request.args.get('trade_uuid')
        
        if trade_uuid:
            cursor.execute("""
                SELECT trade_uuid, price, mfe_value, is_new_high, timestamp, created_at
                FROM realtime_mfe_updates 
                WHERE trade_uuid = %s
                ORDER BY timestamp DESC 
                LIMIT 100
            """, (trade_uuid,))
        else:
            cursor.execute("""
                SELECT trade_uuid, price, mfe_value, is_new_high, timestamp, created_at
                FROM realtime_mfe_updates 
                ORDER BY timestamp DESC 
                LIMIT 200
            """)
        
        updates = []
        for row in cursor.fetchall():
            updates.append({
                'trade_uuid': str(row['trade_uuid']),
                'price': float(row['price']),
                'mfe_value': float(row['mfe_value']),
                'is_new_high': row['is_new_high'],
                'timestamp': row['timestamp'],
                'created_at': row['created_at'].isoformat()
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'mfe_updates': updates,
            'count': len(updates)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# END ENHANCED V2 FUNCTIONS
# ============================================================================
