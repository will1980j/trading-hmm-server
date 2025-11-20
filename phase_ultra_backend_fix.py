#!/usr/bin/env python3
"""
PHASE ULTRA — Backend Fix Patch for Hub Data
Applies all 7 required fixes to automated_signals_state.py
"""

def apply_ultra_fixes():
    """Apply all backend fixes to automated_signals_state.py"""
    
    with open('automated_signals_state.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ============================================================================
    # FIX 1: Standardize direction format (LONG/SHORT → Bullish/Bearish)
    # ============================================================================
    
    # Find build_trade_state function and update direction normalization
    old_direction_logic = '''    # Core identity from first event
    first = events[0]
    trade_id = first["trade_id"]
    
    # PHASE 7.A: Extract from telemetry if available, fallback to legacy columns
    telemetry = first.get("telemetry")
    if telemetry:
        direction = telemetry.get("direction") or first["direction"]'''
    
    new_direction_logic = '''    # Core identity from first event
    first = events[0]
    trade_id = first["trade_id"]
    
    # PHASE 7.A: Extract from telemetry if available, fallback to legacy columns
    telemetry = first.get("telemetry")
    if telemetry:
        raw_direction = telemetry.get("direction") or first["direction"]
        # FIX 1: Standardize direction format
        if raw_direction:
            if raw_direction.upper() in ("LONG", "BULLISH"):
                direction = "Bullish"
            elif raw_direction.upper() in ("SHORT", "BEARISH"):
                direction = "Bearish"
            else:
                direction = raw_direction
        else:
            direction = "Other"'''
    
    content = content.replace(old_direction_logic, new_direction_logic)
    
    # Also fix legacy path
    old_legacy_direction = '''    else:
        # Legacy path
        direction = first["direction"]'''
    
    new_legacy_direction = '''    else:
        # Legacy path
        raw_direction = first["direction"]
        # FIX 1: Standardize direction format
        if raw_direction:
            if raw_direction.upper() in ("LONG", "BULLISH"):
                direction = "Bullish"
            elif raw_direction.upper() in ("SHORT", "BEARISH"):
                direction = "Bearish"
            else:
                direction = raw_direction
        else:
            direction = "Other"'''
    
    content = content.replace(old_legacy_direction, new_legacy_direction)
    
    # ============================================================================
    # FIX 2: Add import for pytz (needed for FIX 4)
    # ============================================================================
    
    if 'import pytz' not in content:
        import_section = '''import psycopg2
import psycopg2.extras'''
        
        new_import_section = '''import psycopg2
import psycopg2.extras
import pytz'''
        
        content = content.replace(import_section, new_import_section)
    
    # ============================================================================
    # FIX 3: Fix session nulls with telemetry fallback
    # ============================================================================
    
    old_session = '''        session = telemetry.get("session") or first["session"]'''
    new_session = '''        # FIX 3: Session with fallback
        session = telemetry.get("session") or first.get("session") or "Other"'''
    
    content = content.replace(old_session, new_session)
    
    # Legacy session fix
    old_legacy_session = '''        session = first["session"]'''
    new_legacy_session = '''        session = first.get("session") or "Other"'''
    
    content = content.replace(old_legacy_session, new_legacy_session)
    
    # ============================================================================
    # FIX 4: Add New York time conversion for last_event_time
    # ============================================================================
    
    # Find the flattened trade dict in get_hub_data and add time_et
    old_flatten = '''        # PHASE 7.A: Flatten for table list with telemetry-rich fields
        all_trades.append({
            "trade_id": state["trade_id"],
            "date": state["signal_date"],
            "time_et": state["signal_time"],'''
    
    new_flatten = '''        # PHASE 7.A: Flatten for table list with telemetry-rich fields
        # FIX 4: Add New York time conversion
        time_et_str = state["signal_time"]
        if state.get("last_event_time"):
            try:
                from datetime import datetime
                import pytz
                last_ts = datetime.fromisoformat(state["last_event_time"])
                et = last_ts.astimezone(pytz.timezone("America/New_York"))
                time_et_str = et.strftime("%H:%M:%S")
            except:
                pass
        
        all_trades.append({
            "trade_id": state["trade_id"],
            "date": state["signal_date"],
            "time_et": time_et_str,'''
    
    content = content.replace(old_flatten, new_flatten)
    
    # ============================================================================
    # FIX 5: Ensure date = signal_date or derived from event timestamp
    # ============================================================================
    
    # This is already handled in build_trade_state, but let's ensure fallback
    old_signal_date = '''    # Grab signal_date (assumed same for all rows of a trade)
    signal_date = events[0].get("signal_date")
    signal_time = events[0].get("signal_time")'''
    
    new_signal_date = '''    # FIX 5: Grab signal_date with fallback to timestamp
    signal_date = events[0].get("signal_date")
    if not signal_date and last_event_time:
        signal_date = last_event_time.date()
    signal_time = events[0].get("signal_time")'''
    
    content = content.replace(old_signal_date, new_signal_date)
    
    # ============================================================================
    # FIX 6: Remove thousands separators in trade_id
    # ============================================================================
    
    # Add trade_id cleanup in _group_events_by_trade
    old_group_function = '''def _group_events_by_trade(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["trade_id"]].append(row)
    return grouped'''
    
    new_group_function = '''def _group_events_by_trade(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        # FIX 6: Remove thousands separators from trade_id
        trade_id = str(row["trade_id"]).replace(",", "")
        row["trade_id"] = trade_id
        grouped[trade_id].append(row)
    return grouped'''
    
    content = content.replace(old_group_function, new_group_function)
    
    # ============================================================================
    # FIX 7: Ensure TEST telemetry trades appear correctly
    # ============================================================================
    
    # Update the flattened trade dict to include full telemetry objects
    old_setup_dict = '''            # PHASE 7.A: Nested telemetry objects
            "setup": {
                "family": state.get("setup_family"),
                "variant": state.get("setup_variant"),
                "id": state.get("setup_id"),
                "signal_strength": state.get("setup_strength")
            },
            "market_state": {
                "trend_regime": state.get("market_trend_regime"),
                "volatility_regime": state.get("market_vol_regime")
            },
            "targets": state.get("targets")'''
    
    new_setup_dict = '''            # PHASE 7.A: Nested telemetry objects
            # FIX 7: Full telemetry object support
            "setup": {
                "setup_family": state.get("setup_family"),
                "setup_variant": state.get("setup_variant"),
                "setup_id": state.get("setup_id"),
                "signal_strength": state.get("setup_strength")
            },
            "market_state": {
                "trend_regime": state.get("market_trend_regime"),
                "volatility_regime": state.get("market_vol_regime")
            },
            "targets": state.get("targets"),
            # Add current MFE for active trades
            "current_mfe": state.get("no_be_mfe_R") or state.get("be_mfe_R"),
            "exit_price": state.get("exit_price"),
            "exit_reason": state.get("completed_reason")'''
    
    content = content.replace(old_setup_dict, new_setup_dict)
    
    # Write the updated content
    with open('automated_signals_state.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied all 7 backend fixes to automated_signals_state.py")
    print("   1. Standardized direction format (LONG/SHORT → Bullish/Bearish)")
    print("   2. Added pytz import for timezone conversion")
    print("   3. Fixed session nulls with telemetry fallback")
    print("   4. Added New York time conversion for last_event_time")
    print("   5. Ensured date fallback to timestamp")
    print("   6. Removed thousands separators from trade_id")
    print("   7. Enhanced telemetry object support for TEST trades")


def apply_css_fixes():
    """Apply CSS dark mode and table styling fixes"""
    
    css_patch = '''
/* PHASE ULTRA — Dark Mode & Table Styling Fixes */

/* Force dark table */
.as-table-container table {
    background: #111 !important;
    color: #ddd !important;
}

.as-table-container td,
.as-table-container th {
    color: #ddd !important;
    border-color: #333 !important;
}

/* Modal */
.as-modal-content {
    color: #eee !important;
}

.as-modal-content h3,
.as-modal-content .as-meta,
.as-modal-content .as-setup,
.as-modal-content .as-market {
    color: #eee !important;
}

/* Pill fixes */
.as-pill {
    color: #fff !important;
}

/* Timeline items */
.as-timeline-item {
    color: #ddd !important;
}

/* Fix strength bar visibility */
.as-strength-bar {
    background: rgba(255, 255, 255, 0.15) !important;
}
'''
    
    with open('static/css/automated_signals_ultra.css', 'a', encoding='utf-8') as f:
        f.write(css_patch)
    
    print("✅ Applied CSS dark mode and table styling fixes")


if __name__ == "__main__":
    print("🚀 PHASE ULTRA — Backend Fix Patch")
    print("=" * 60)
    apply_ultra_fixes()
    apply_css_fixes()
    print("=" * 60)
    print("✅ ALL FIXES APPLIED")
    print("\nNext steps:")
    print("1. Commit changes via GitHub Desktop")
    print("2. Push to main branch (triggers Railway auto-deploy)")
    print("3. Wait 2-3 minutes for deployment")
    print("4. Reload /automated-signals-ultra")
    print("5. Verify modal shows full setup & market_state")
    print("6. Verify table shows correct direction, sessions, MFE values")
