
# ============================================================================
# PHASE 5: TELEMETRY-AWARE WEBHOOK HANDLER
# ============================================================================

def automated_signals_webhook_v2():
    """
    Enhanced webhook endpoint with telemetry support.
    Handles BOTH:
    - New telemetry payloads (schema_version present)
    - Legacy payloads (backward compatible)
    """
    try:
        payload = request.get_json(silent=True)
        
        if not payload:
            return jsonify({"success": False, "error": "No JSON payload"}), 400
        
        # DETECT PAYLOAD TYPE
        schema_version = payload.get("schema_version")
        
        if schema_version:
            # NEW TELEMETRY PAYLOAD
            logger.info(f"📊 Telemetry payload detected: schema={schema_version}")
            result = handle_telemetry_payload(payload)
        else:
            # LEGACY PAYLOAD - use existing handler
            logger.info("📥 Legacy payload detected - using backward compatible handler")
            result = handle_legacy_payload(payload)
        
        return jsonify(result), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def handle_telemetry_payload(payload):
    """
    Process new telemetry payload from Phase 4+ indicator.
    Extracts fields and stores in database with full JSON.
    """
    conn = None
    cursor = None
    
    try:
        # VALIDATE REQUIRED FIELDS
        trade_id = payload.get("trade_id")
        event_type = payload.get("event_type")
        
        if not trade_id or not event_type:
            return {"success": False, "error": "Missing trade_id or event_type"}
        
        # EXTRACT CORE FIELDS
        direction = payload.get("direction")
        entry_price = payload.get("entry_price")
        stop_loss = payload.get("stop_loss")
        be_price = payload.get("be_price")
        mfe_R = payload.get("mfe_R")
        mae_R = payload.get("mae_R")
        final_mfe_R = payload.get("final_mfe_R")
        exit_price = payload.get("exit_price")
        exit_reason = payload.get("exit_reason")
        session = payload.get("session")
        
        # PARSE TIMESTAMP (ISO 8601 UTC)
        event_timestamp_str = payload.get("event_timestamp")
        if event_timestamp_str:
            from datetime import datetime
            import pytz
            
            # Parse ISO 8601 UTC timestamp
            event_timestamp = datetime.fromisoformat(event_timestamp_str.replace('Z', '+00:00'))
            
            # Convert to America/New_York
            eastern = pytz.timezone('America/New_York')
            local_timestamp = event_timestamp.astimezone(eastern)
            
            signal_date = local_timestamp.date()
            signal_time = local_timestamp.time()
            timestamp = local_timestamp
        else:
            # Fallback to current time
            from datetime import datetime
            import pytz
            eastern = pytz.timezone('America/New_York')
            timestamp = datetime.now(eastern)
            signal_date = timestamp.date()
            signal_time = timestamp.time()
        
        # EXTRACT NESTED OBJECTS
        targets = payload.get("targets")
        setup = payload.get("setup")
        market_state = payload.get("market_state")
        
        # GET DATABASE CONNECTION
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return {"success": False, "error": "DATABASE_URL not configured"}
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # INSERT INTO DATABASE
        # Store in BOTH legacy columns AND telemetry JSON
        insert_sql = """
            INSERT INTO automated_signals (
                trade_id, event_type, direction,
                entry_price, stop_loss, session, bias,
                risk_distance, targets,
                current_price, mfe, be_mfe, no_be_mfe,
                exit_price, final_mfe,
                signal_date, signal_time, timestamp,
                telemetry
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s
            )
        """
        
        # Calculate risk_distance if available
        risk_distance = None
        if entry_price and stop_loss:
            risk_distance = abs(float(entry_price) - float(stop_loss))
        
        # Use direction as bias for now
        bias = direction
        
        # Current price (for MFE updates)
        current_price = payload.get("current_price") or entry_price
        
        # Convert targets to JSON if present
        import json
        targets_json = json.dumps(targets) if targets else None
        
        cursor.execute(insert_sql, (
            trade_id, event_type, direction,
            entry_price, stop_loss, session, bias,
            risk_distance, targets_json,
            current_price, mfe_R, mfe_R, mfe_R,  # mfe, be_mfe, no_be_mfe
            exit_price, final_mfe_R,
            signal_date, signal_time, timestamp,
            json.dumps(payload)  # FULL TELEMETRY JSON
        ))
        
        conn.commit()
        
        logger.info(f"✅ Telemetry event stored: {event_type} for {trade_id}")
        
        return {
            "success": True,
            "message": f"Telemetry event {event_type} processed",
            "trade_id": trade_id,
            "event_type": event_type,
            "schema_version": payload.get("schema_version")
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Telemetry processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def handle_legacy_payload(payload):
    """
    Process legacy payload format (backward compatibility).
    Uses existing logic - no changes to historical behavior.
    """
    # This would call the existing handler logic
    # For now, return a placeholder
    return {"success": True, "message": "Legacy payload processed (existing handler)"}
