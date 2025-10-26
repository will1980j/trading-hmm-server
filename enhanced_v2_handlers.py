
# ============================================================================
# ENHANCED WEBHOOK HANDLERS (MODIFY EXISTING ENDPOINTS)
# ============================================================================

# Modify existing /api/live-signals-v2 endpoint
def enhanced_receive_signal_v2():
    """Enhanced V2 signal processing with comprehensive data handling"""
    try:
        # Get raw data from TradingView
        raw_data = request.get_data(as_text=True)
        logger.info(f"[V2 ENHANCED] Raw webhook data: {raw_data}")
        
        # Parse JSON data from Enhanced FVG Indicator
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            # Handle plain text format if needed
            data = {"raw_message": raw_data}
        
        logger.info(f"[V2 ENHANCED] Parsed data: {data}")
        
        # Process through enhanced V2 system
        signal_data = process_enhanced_signal_data_v2(data)
        
        if "error" in signal_data:
            return jsonify({
                "success": False,
                "error": signal_data["error"],
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Store in enhanced V2 database
        storage_result = store_enhanced_v2_signal(signal_data)
        
        if "error" in storage_result:
            return jsonify({
                "success": False,
                "error": storage_result["error"],
                "timestamp": datetime.now().isoformat()
            }), 500
        
        # Also maintain compatibility with existing system
        try:
            # Store in original live_signals table for compatibility
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO live_signals (symbol, type, timestamp, price, session, bias)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                data.get('symbol', 'NQ1!'),
                data.get('signal_type', ''),
                datetime.now(),
                data.get('price', 0),
                data.get('session', 'NY AM'),
                data.get('signal_type', '')
            ))
            
            original_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as original_error:
            logger.warning(f"Original table storage failed: {str(original_error)}")
            original_id = None
        
        return jsonify({
            "success": True,
            "message": "Enhanced V2 signal processed successfully",
            "signal_id": storage_result["signal_id"],
            "trade_uuid": storage_result["trade_uuid"],
            "original_signal_id": original_id,
            "automation_level": "enhanced_v2",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"[V2 ENHANCED ERROR] {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Modify existing /api/realtime-price endpoint
def enhanced_receive_realtime_price():
    """Enhanced real-time price processing with V2 MFE tracking"""
    try:
        # Get raw data from TradingView 1-second indicator
        raw_data = request.get_data(as_text=True)
        logger.info(f"[V2 PRICE] Raw price data: {raw_data}")
        
        # Parse JSON data
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = {"raw_message": raw_data}
        
        # Process through enhanced V2 price system
        price_result = process_realtime_price_v2(data)
        
        if "error" in price_result:
            return jsonify({
                "status": "error",
                "message": price_result["error"],
                "timestamp": datetime.now().isoformat()
            }), 500
        
        return jsonify({
            "status": "success",
            "price": price_result["price"],
            "price_id": price_result["price_id"],
            "mfe_updates": price_result["mfe_updates"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"[V2 PRICE ERROR] {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ============================================================================
# END ENHANCED WEBHOOK HANDLERS
# ============================================================================
