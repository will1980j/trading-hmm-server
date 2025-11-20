
# ============================================================================
# PHASE 5: TELEMETRY-AWARE TRADE STATE BUILDER
# ============================================================================

def build_trade_state_v2(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Enhanced trade state builder with telemetry support.
    Prefers telemetry JSON when available, falls back to legacy columns.
    """
    if not events:
        return None
    
    # Core identity from first event
    first = events[0]
    trade_id = first["trade_id"]
    
    # Check if telemetry is available
    has_telemetry = first.get("telemetry") is not None
    
    if has_telemetry:
        # TELEMETRY PATH - prefer JSON fields
        telemetry = first["telemetry"]
        direction = telemetry.get("direction") or first.get("direction")
        session = telemetry.get("session") or first.get("session")
        entry_price = telemetry.get("entry_price") or first.get("entry_price")
        stop_loss = telemetry.get("stop_loss") or first.get("stop_loss")
        
        # Extract nested objects
        targets = telemetry.get("targets")
        setup = telemetry.get("setup")
        market_state = telemetry.get("market_state")
    else:
        # LEGACY PATH - use flat columns
        direction = first.get("direction")
        session = first.get("session")
        entry_price = first.get("entry_price")
        stop_loss = first.get("stop_loss")
        targets = None
        setup = None
        market_state = None
    
    # Derived state
    status = "UNKNOWN"
    current_mfe = None
    final_mfe = None
    exit_price = None
    exit_reason = None
    
    # Process all events
    for row in events:
        etype = row["event_type"]
        
        # Check for telemetry
        if row.get("telemetry"):
            tel = row["telemetry"]
            
            # Extract MFE from telemetry
            if tel.get("mfe_R") is not None:
                current_mfe = float(tel["mfe_R"])
            
            # Extract exit info from telemetry
            if tel.get("final_mfe_R") is not None:
                final_mfe = float(tel["final_mfe_R"])
            if tel.get("exit_price") is not None:
                exit_price = float(tel["exit_price"])
            if tel.get("exit_reason"):
                exit_reason = tel["exit_reason"]
        else:
            # Fallback to legacy columns
            if row.get("mfe") is not None:
                current_mfe = float(row["mfe"])
            if row.get("final_mfe") is not None:
                final_mfe = float(row["final_mfe"])
            if row.get("exit_price") is not None:
                exit_price = float(row["exit_price"])
        
        # Update status based on event type
        if etype == "ENTRY":
            status = "ACTIVE"
        elif etype == "MFE_UPDATE":
            status = "ACTIVE"
        elif etype == "BE_TRIGGERED":
            status = "BE_PROTECTED"
        elif etype in ("EXIT_STOP_LOSS", "EXIT_BREAK_EVEN", "EXIT_TAKE_PROFIT"):
            status = "COMPLETED"
    
    # Build trade state
    trade_state = {
        "trade_id": trade_id,
        "direction": direction,
        "session": session,
        "status": status,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "current_mfe": current_mfe,
        "final_mfe": final_mfe,
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "targets": targets,
        "setup": setup,
        "market_state": market_state
    }
    
    return trade_state
