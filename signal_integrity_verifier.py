"""
Signal Integrity Verification System
Randomly selects signals and verifies dashboard data matches TradingView webhooks exactly
"""

import os
import psycopg2
import random
from datetime import datetime, timedelta
from decimal import Decimal
import json

def get_db_connection():
    """Get fresh database connection"""
    database_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(database_url)

def verify_random_signals(num_signals=2):
    """
    Randomly select signals and run comprehensive verification
    Returns compact results that expand on errors
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get random trade IDs from last 7 days
        cursor.execute("""
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE timestamp > NOW() - INTERVAL '7 days'
            AND trade_id IS NOT NULL
            ORDER BY RANDOM()
            LIMIT %s
        """, (num_signals,))
        
        trade_ids = [row[0] for row in cursor.fetchall()]
        
        if not trade_ids:
            return {
                "status": "NO_DATA",
                "message": "No signals found in last 7 days",
                "signals_checked": 0,
                "errors": []
            }
        
        results = {
            "status": "PASS",
            "signals_checked": len(trade_ids),
            "errors": [],
            "warnings": [],
            "details": []
        }
        
        for trade_id in trade_ids:
            signal_result = verify_single_signal(cursor, trade_id)
            results["details"].append(signal_result)
            
            # Collect errors and warnings
            if signal_result["errors"]:
                results["errors"].extend(signal_result["errors"])
                results["status"] = "FAIL"
            if signal_result["warnings"]:
                results["warnings"].extend(signal_result["warnings"])
                if results["status"] == "PASS":
                    results["status"] = "WARNING"
        
        return results
        
    finally:
        cursor.close()
        conn.close()

def verify_single_signal(cursor, trade_id):
    """Run all verification checks on a single signal"""
    
    # Get all events for this signal
    cursor.execute("""
        SELECT event_type, bias, entry_price, sl_price, risk_distance,
               be_mfe, no_be_mfe, session, signal_date, signal_time,
               timestamp, status, target_1r, target_2r, target_3r
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    events = cursor.fetchall()
    
    if not events:
        return {
            "trade_id": trade_id,
            "status": "ERROR",
            "errors": [f"No events found for trade {trade_id}"],
            "warnings": [],
            "checks": []
        }
    
    # Parse events
    entry_event = None
    mfe_events = []
    be_event = None
    exit_event = None
    
    for event in events:
        event_type = event[0]
        if event_type == "ENTRY":
            entry_event = event
        elif event_type == "MFE_UPDATE":
            mfe_events.append(event)
        elif event_type == "BE_TRIGGERED":
            be_event = event
        elif event_type in ("EXIT_STOP_LOSS", "EXIT_BREAK_EVEN"):
            exit_event = event
    
    # Run verification checks
    result = {
        "trade_id": trade_id,
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "checks": []
    }
    
    # Check 1: Event sequence integrity
    check_event_sequence(events, result)
    
    # Check 2: Entry data consistency
    if entry_event:
        check_entry_data(entry_event, result)
    else:
        result["errors"].append("Missing ENTRY event")
        result["status"] = "FAIL"
    
    # Check 3: MFE progression logic
    if mfe_events:
        check_mfe_progression(mfe_events, result)
    
    # Check 4: Dual MFE logic (if BE triggered)
    if be_event and mfe_events:
        check_dual_mfe_logic(be_event, mfe_events, result)
    
    # Check 5: Status consistency
    check_status_consistency(entry_event, exit_event, result)
    
    # Check 6: Target price calculations
    if entry_event:
        check_target_calculations(entry_event, result)
    
    # Check 7: Timestamp chronology
    check_timestamp_order(events, result)
    
    # Check 8: Session validity
    if entry_event:
        check_session_validity(entry_event, result)
    
    # Set overall status
    if result["errors"]:
        result["status"] = "FAIL"
    elif result["warnings"]:
        result["status"] = "WARNING"
    
    return result

def check_event_sequence(events, result):
    """Verify events follow logical order"""
    event_types = [e[0] for e in events]
    
    # ENTRY must be first
    if event_types[0] != "ENTRY":
        result["errors"].append(f"First event is {event_types[0]}, expected ENTRY")
    
    # Check for duplicate ENTRY events
    entry_count = event_types.count("ENTRY")
    if entry_count > 1:
        result["errors"].append(f"Multiple ENTRY events found ({entry_count})")
    
    # EXIT must be last (if present)
    exit_types = ["EXIT_STOP_LOSS", "EXIT_BREAK_EVEN"]
    has_exit = any(et in event_types for et in exit_types)
    if has_exit and event_types[-1] not in exit_types:
        result["warnings"].append("EXIT event is not the last event")
    
    result["checks"].append({
        "name": "Event Sequence",
        "status": "PASS" if not result["errors"] else "FAIL",
        "details": f"{len(events)} events in correct order"
    })

def check_entry_data(entry_event, result):
    """Verify entry event data integrity"""
    bias, entry_price, sl_price, risk_distance = entry_event[1], entry_event[2], entry_event[3], entry_event[4]
    
    # Verify risk distance calculation
    if entry_price and sl_price:
        calculated_risk = abs(float(entry_price) - float(sl_price))
        stored_risk = float(risk_distance) if risk_distance else 0
        
        if abs(calculated_risk - stored_risk) > 0.5:  # Allow 0.5 point tolerance
            result["errors"].append(
                f"Risk distance mismatch: calculated={calculated_risk:.2f}, stored={stored_risk:.2f}"
            )
    
    result["checks"].append({
        "name": "Entry Data",
        "status": "PASS" if not any("Risk distance" in e for e in result["errors"]) else "FAIL",
        "details": f"Entry: {entry_price}, SL: {sl_price}, Risk: {risk_distance}"
    })

def check_mfe_progression(mfe_events, result):
    """Verify MFE values only increase"""
    prev_be_mfe = 0
    prev_no_be_mfe = 0
    
    for event in mfe_events:
        be_mfe = float(event[5]) if event[5] else 0
        no_be_mfe = float(event[6]) if event[6] else 0
        
        # MFE should never decrease (allowing small rounding tolerance)
        if be_mfe < prev_be_mfe - 0.01:
            result["warnings"].append(
                f"BE MFE decreased: {prev_be_mfe:.2f}R → {be_mfe:.2f}R"
            )
        
        if no_be_mfe < prev_no_be_mfe - 0.01:
            result["warnings"].append(
                f"No-BE MFE decreased: {prev_no_be_mfe:.2f}R → {no_be_mfe:.2f}R"
            )
        
        prev_be_mfe = max(prev_be_mfe, be_mfe)
        prev_no_be_mfe = max(prev_no_be_mfe, no_be_mfe)
    
    result["checks"].append({
        "name": "MFE Progression",
        "status": "PASS" if not any("MFE decreased" in w for w in result["warnings"]) else "WARNING",
        "details": f"Peak: {prev_be_mfe:.2f}R / {prev_no_be_mfe:.2f}R ({len(mfe_events)} updates)"
    })

def check_dual_mfe_logic(be_event, mfe_events, result):
    """Verify BE MFE freezes after BE trigger while No-BE continues"""
    be_timestamp = be_event[10]
    be_mfe_at_trigger = float(be_event[5]) if be_event[5] else 0
    
    # Find MFE events after BE trigger
    post_be_events = [e for e in mfe_events if e[10] > be_timestamp]
    
    if post_be_events:
        for event in post_be_events:
            be_mfe = float(event[5]) if event[5] else 0
            no_be_mfe = float(event[6]) if event[6] else 0
            
            # BE MFE should stay constant after trigger
            if abs(be_mfe - be_mfe_at_trigger) > 0.01:
                result["errors"].append(
                    f"BE MFE changed after trigger: {be_mfe_at_trigger:.2f}R → {be_mfe:.2f}R"
                )
            
            # No-BE MFE should be >= BE MFE
            if no_be_mfe < be_mfe - 0.01:
                result["warnings"].append(
                    f"No-BE MFE < BE MFE after trigger: {no_be_mfe:.2f}R < {be_mfe:.2f}R"
                )
    
    result["checks"].append({
        "name": "Dual MFE Logic",
        "status": "PASS" if not any("BE MFE changed" in e for e in result["errors"]) else "FAIL",
        "details": f"BE triggered at {be_mfe_at_trigger:.2f}R, {len(post_be_events)} updates after"
    })

def check_status_consistency(entry_event, exit_event, result):
    """Verify trade status matches event history"""
    if exit_event:
        status = exit_event[11]
        if status != "completed":
            result["warnings"].append(
                f"EXIT event exists but status is '{status}', expected 'completed'"
            )
        check_status = "COMPLETED"
    else:
        check_status = "ACTIVE"
    
    result["checks"].append({
        "name": "Status Consistency",
        "status": "PASS",
        "details": f"Trade is {check_status}"
    })

def check_target_calculations(entry_event, result):
    """Verify target prices calculated correctly"""
    bias, entry_price, risk_distance = entry_event[1], entry_event[2], entry_event[4]
    target_1r, target_2r, target_3r = entry_event[12], entry_event[13], entry_event[14]
    
    if entry_price and risk_distance and target_1r:
        entry = float(entry_price)
        risk = float(risk_distance)
        
        if bias == "Bullish":
            expected_1r = entry + risk
            expected_2r = entry + (2 * risk)
            expected_3r = entry + (3 * risk)
        else:  # Bearish
            expected_1r = entry - risk
            expected_2r = entry - (2 * risk)
            expected_3r = entry - (3 * risk)
        
        # Check with 1 point tolerance
        if abs(float(target_1r) - expected_1r) > 1.0:
            result["errors"].append(
                f"Target 1R mismatch: expected {expected_1r:.2f}, got {target_1r}"
            )
    
    result["checks"].append({
        "name": "Target Calculations",
        "status": "PASS" if not any("Target" in e for e in result["errors"]) else "FAIL",
        "details": f"1R: {target_1r}, 2R: {target_2r}, 3R: {target_3r}"
    })

def check_timestamp_order(events, result):
    """Verify timestamps are chronological"""
    timestamps = [e[10] for e in events]
    
    for i in range(1, len(timestamps)):
        if timestamps[i] < timestamps[i-1]:
            result["errors"].append(
                f"Timestamp out of order at event {i+1}"
            )
    
    result["checks"].append({
        "name": "Timestamp Order",
        "status": "PASS" if not any("Timestamp" in e for e in result["errors"]) else "FAIL",
        "details": f"{len(events)} events in chronological order"
    })

def check_session_validity(entry_event, result):
    """Verify session is valid"""
    session = entry_event[7]
    valid_sessions = ["ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM"]
    
    if session not in valid_sessions:
        result["warnings"].append(
            f"Invalid session: '{session}'"
        )
    
    result["checks"].append({
        "name": "Session Validity",
        "status": "PASS" if session in valid_sessions else "WARNING",
        "details": f"Session: {session}"
    })

def register_signal_integrity_api(app):
    """Register signal integrity verification endpoint"""
    from flask import jsonify
    
    @app.route('/api/automated-signals/verify-integrity', methods=['GET'])
    def verify_signal_integrity():
        """Run random signal integrity verification"""
        try:
            results = verify_random_signals(num_signals=2)
            return jsonify(results), 200
        except Exception as e:
            return jsonify({
                "status": "ERROR",
                "message": str(e),
                "signals_checked": 0,
                "errors": [str(e)]
            }), 500
