# automated_signals_state.py
## Pure backend logic for the Automated Signals Hub.
# - Reads rows from the automated_signals table
# - Folds events into canonical trade state
# - Builds calendar + trade list views
## THIS MODULE MUST NEVER WRITE TO THE DATABASE.
# READ-ONLY ONLY.
# INTEGRITY_REPAIR_STATE_ACTIVE

def auto_guard_webhook_payload(payload):
    """
    Phase E1: Auto-Guard Normalization Layer
    Ensures required fields exist BEFORE parsing.
    Returns (clean_payload, error_message or None)
    """
    if not isinstance(payload, dict):
        return None, "Invalid payload: not a JSON object."
    
    # Required fields for ENTRY
    required_base = ["event_type", "trade_id"]
    for field in required_base:
        if payload.get(field) in (None, "", "null"):
            return None, f"Missing required field: {field}"
    
    evt = payload.get("event_type")
    
    # Guards for ENTRY
    if evt == "ENTRY":
        for f in ["direction", "entry_price", "stop_loss", "risk_distance"]:
            if payload.get(f) in (None, "", "null"):
                return None, f"Invalid ENTRY: missing field {f}"
    
    # Guards for MFE updates
    if evt == "MFE_UPDATE":
        # Ensure numeric MFE values
        for f in ["be_mfe", "no_be_mfe"]:
            try:
                if payload.get(f) is not None:
                    float(payload.get(f))
            except Exception:
                return None, f"Malformed MFE value: {f}"
    
    # Guards for EXIT events
    if evt in ("EXIT_BE", "EXIT_SL"):
        if payload.get("exit_price") in (None, "", "null"):
            return None, "Missing exit_price"
    
    return payload, None

import os
from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras
import pytz


# --- DB helpers -------------------------------------------------------------

def _get_db_conn():
    """Return a fresh PostgreSQL connection using DATABASE_URL.
    This respects the cloud-first rule: always connect to Railway Postgres,
    never localhost."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in environment")
    return psycopg2.connect(database_url)


def _decimal_to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


# --- Event → Trade state fold ----------------------------------------------

def build_trade_state(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Fold a list of automated_signals rows (dicts) into a single canonical
    trade state object.
    `events` MUST already be sorted by timestamp ascending.
    PHASE 7.A: Enhanced with telemetry extraction for setup, market_state, and targets."""
    if not events:
        return None

    # Core identity from first event
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
            direction = "Other"
        # FIX 3: Session with fallback
        session = telemetry.get("session") or first.get("session") or "Other"
        entry_price = _decimal_to_float(telemetry.get("entry_price") or first.get("entry_price"))
        stop_loss = _decimal_to_float(telemetry.get("stop_loss") or first.get("stop_loss"))
        targets = telemetry.get("targets") or first.get("targets")
        
        # Extract setup information
        setup = telemetry.get("setup", {})
        setup_family = setup.get("setup_family")
        setup_variant = setup.get("setup_variant")
        setup_id = setup.get("setup_id")
        setup_strength = setup.get("signal_strength")
        
        # Extract market state at entry
        market_state = telemetry.get("market_state", {})
        market_trend_regime = market_state.get("trend_regime")
        market_vol_regime = market_state.get("volatility_regime")
    else:
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
            direction = "Other"
        session = first.get("session") or "Other"
        entry_price = _decimal_to_float(first.get("entry_price"))
        stop_loss = _decimal_to_float(first.get("stop_loss"))
        targets = first.get("targets")
        
        # No telemetry - setup fields will be None
        setup_family = None
        setup_variant = None
        setup_id = None
        setup_strength = None
        market_trend_regime = None
        market_vol_regime = None
    
    bias = first.get("bias")
    risk_distance = _decimal_to_float(first.get("risk_distance"))

    # Derived state
    status = "UNKNOWN"  # ACTIVE | BE_PROTECTED | COMPLETED | CANCELLED
    entry_time: Optional[datetime] = None
    last_event_time: Optional[datetime] = None
    current_be_mfe = None  # last known BE MFE
    current_no_be_mfe = None  # last known No-BE MFE
    max_be_mfe = None
    max_no_be_mfe = None
    exit_price = None
    final_mfe = None
    completed_reason = None  # e.g. EXIT_SL, EXIT_BE, EXIT_TP, CANCELLED

    for row in events:
        etype = row["event_type"]
        ts: datetime = row["timestamp"]
        last_event_time = ts

        # Use first event timestamp as entry_time if not explicitly separate
        if entry_time is None:
            entry_time = ts

        # Live MFE tracking
        be_mfe_val = row.get("be_mfe")
        no_be_mfe_val = row.get("no_be_mfe")
        if be_mfe_val is not None:
            current_be_mfe = _decimal_to_float(be_mfe_val)
            if max_be_mfe is None or current_be_mfe > max_be_mfe:
                max_be_mfe = current_be_mfe
        if no_be_mfe_val is not None:
            current_no_be_mfe = _decimal_to_float(no_be_mfe_val)
            if max_no_be_mfe is None or current_no_be_mfe > max_no_be_mfe:
                max_no_be_mfe = current_no_be_mfe

        # Event-type based state transitions
        # NOTE: event_type strings must match what the webhook writes.
        if etype == "SIGNAL_CREATED":
            # Trade is now live
            status = "ACTIVE"
            # If entry_time is specifically encoded in this row, prefer that
            # (otherwise we keep the first timestamp)
            if row.get("signal_time"):
                # signal_time is a time-only field, but timestamp already has full
                # datetime in ET, so we keep timestamp as canonical.
                pass

        elif etype == "MFE_UPDATE":
            # Trade remains ACTIVE or BE_PROTECTED; no state change
            if status == "UNKNOWN":
                status = "ACTIVE"

        elif etype == "BE_TRIGGERED":
            # Trade is now protected at BE but still LIVE
            status = "BE_PROTECTED"

        # COMPLETION EVENTS — based on actual event types in the database
        elif etype in ("EXIT_BREAK_EVEN", "EXIT_STOP_LOSS"):
            status = "COMPLETED"
            completed_reason = etype
            
            # Determine exit price
            ep = row.get("exit_price") or row.get("current_price")
            if ep is not None:
                exit_price = _decimal_to_float(ep)
            
            # MFE logic
            # Break-even exit: final R = 0
            if etype == "EXIT_BREAK_EVEN":
                final_mfe = 0.0
            
            # Stop-loss exit: final R = -1R (or use recorded MFE if available)
            elif etype == "EXIT_STOP_LOSS":
                # If indicator provides final_mfe, use it
                if row.get("final_mfe") is not None:
                    final_mfe = _decimal_to_float(row["final_mfe"])
                # Else compute final R from exit vs entry SL distance
                elif current_no_be_mfe is not None:
                    final_mfe = current_no_be_mfe
                elif current_be_mfe is not None:
                    final_mfe = current_be_mfe
                else:
                    # Default: STOP LOSS = -1R
                    final_mfe = -1.0

        elif etype == "CANCELLED":
            status = "CANCELLED"
            completed_reason = "CANCELLED"

        # Future: handle STATE_SNAPSHOT, etc. (non-terminal reconciliations)

    # FIX 1: Determine trade status using explicit EXIT events only
    has_exit_event = any(e.get("event_type") in ("EXIT_BREAK_EVEN", "EXIT_STOP_LOSS")
                         for e in events)
    if has_exit_event:
        status = "COMPLETED"
    elif any(e.get("event_type") == "BE_TRIGGERED" for e in events):
        status = "BE_PROTECTED"
    else:
        status = "ACTIVE"

    # For calendar / summary stats, we want a "max_mfe" concept.
    # Use No-BE as primary because it reflects full excursion, backed up by BE MFE.
    max_mfe_for_stats = max_no_be_mfe
    if max_mfe_for_stats is None:
        max_mfe_for_stats = max_be_mfe

    # FIX 5: Grab signal_date with fallback to timestamp
    signal_date = events[0].get("signal_date")
    if not signal_date and last_event_time:
        signal_date = last_event_time.date()
    signal_time = events[0].get("signal_time")

    trade_state = {
        "trade_id": trade_id,
        "direction": direction,
        "session": session,
        "bias": bias,
        "status": status,
        "completed_reason": completed_reason,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "risk_distance": risk_distance,
        "targets": targets,
        "entry_time": entry_time.isoformat() if entry_time else None,
        "last_event_time": last_event_time.isoformat() if last_event_time else None,
        "signal_date": str(signal_date) if isinstance(signal_date, (date, datetime)) else signal_date,
        "signal_time": str(signal_time) if signal_time is not None else None,
        "be_mfe_R": current_be_mfe,
        "no_be_mfe_R": current_no_be_mfe,
        "max_be_mfe_R": max_be_mfe,
        "max_no_be_mfe_R": max_no_be_mfe,
        "max_mfe_for_stats": max_mfe_for_stats,
        "exit_price": exit_price,
        "final_mfe_R": final_mfe,
        # PHASE 7.A: Telemetry-rich fields
        "setup_family": setup_family,
        "setup_variant": setup_variant,
        "setup_id": setup_id,
        "setup_strength": setup_strength,
        "market_trend_regime": market_trend_regime,
        "market_vol_regime": market_vol_regime,
    }
    return trade_state


# --- Hub data builders ------------------------------------------------------

def _fetch_events_for_range(
    conn,
    start_date: Optional[str],
    end_date: Optional[str],
) -> List[Dict[str, Any]]:
    """Fetch all automated_signals rows within [start_date, end_date].
    Dates are inclusive; if None, the range is unbounded on that side.
    PHASE 7.A: Now includes telemetry JSONB column."""
    where_clauses = []
    params: List[Any] = []
    if start_date:
        where_clauses.append("signal_date >= %s")
        params.append(start_date)
    if end_date:
        where_clauses.append("signal_date <= %s")
        params.append(end_date)

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    sql = f"""
    SELECT
        id,
        trade_id,
        event_type,
        direction,
        entry_price,
        stop_loss,
        session,
        bias,
        risk_distance,
        current_price,
        mfe,
        exit_price,
        final_mfe,
        timestamp,
        signal_date,
        signal_time,
        be_mfe,
        no_be_mfe
    FROM automated_signals
    {where_sql}
    ORDER BY trade_id, timestamp ASC, id ASC
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return rows


def _group_events_by_trade(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        # FIX 6: Remove thousands separators from trade_id
        trade_id = str(row["trade_id"]).replace(",", "")
        row["trade_id"] = trade_id
        grouped[trade_id].append(row)
    return grouped


def build_calendar_view(trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate trades into calendar-style stats per signal_date."""
    by_date: Dict[str, Dict[str, Any]] = {}
    for trade in trades:
        # Use either 'date' (flattened field) or 'signal_date'
        date_key = trade.get("date") or trade.get("signal_date")
        if not date_key:
            # Skip trades with no date — cannot place on calendar
            continue
        stats = by_date.get(date_key)
        if not stats:
            stats = {
                "date": date_key,
                "trade_count": 0,
                "sum_be_mfe": 0.0,
                "sum_no_be_mfe": 0.0,
                "sum_max_mfe": 0.0,
                "max_no_be_mfe": None,
                "min_no_be_mfe": None,
            }
            by_date[date_key] = stats

        stats["trade_count"] += 1
        be_val = trade.get("max_be_mfe_R")
        no_be_val = trade.get("max_no_be_mfe_R")
        max_mfe_val = trade.get("max_mfe_for_stats")

        if be_val is not None:
            stats["sum_be_mfe"] += be_val
        if no_be_val is not None:
            stats["sum_no_be_mfe"] += no_be_val
            if stats["max_no_be_mfe"] is None or no_be_val > stats["max_no_be_mfe"]:
                stats["max_no_be_mfe"] = no_be_val
            if stats["min_no_be_mfe"] is None or no_be_val < stats["min_no_be_mfe"]:
                stats["min_no_be_mfe"] = no_be_val
        if max_mfe_val is not None:
            stats["sum_max_mfe"] += max_mfe_val

    # Convert to list with averages
    calendar: List[Dict[str, Any]] = []
    for date_key, stats in sorted(by_date.items()):
        count = stats["trade_count"]
        calendar.append({
            "date": date_key,
            "trade_count": count,
            "avg_be_mfe_R": (stats["sum_be_mfe"] / count) if count and stats["sum_be_mfe"] else None,
            "avg_no_be_mfe_R": (stats["sum_no_be_mfe"] / count) if count and stats["sum_no_be_mfe"] else None,
            "avg_max_mfe_R": (stats["sum_max_mfe"] / count) if count and stats["sum_max_mfe"] else None,
            "max_no_be_mfe_R": stats["max_no_be_mfe"],
            "min_no_be_mfe_R": stats["min_no_be_mfe"],
        })
    return calendar


def _apply_filters(
    trade: Dict[str, Any],
    session: Optional[str],
    direction: Optional[str],
    status: Optional[str],
) -> bool:
    if session and session != "ALL":
        if trade["session"] != session:
            return False
    if direction and direction != "ALL":
        if trade["direction"] != direction:
            return False
    if status and status != "ALL":
        if trade["status"] != status:
            return False
    return True


def get_hub_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session: Optional[str] = None,
    direction: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Main entry for the Automated Signals Hub dashboard.
    Returns:
    {
        "calendar": [...],
        "trades": [...]
    }
    """
    conn = _get_db_conn()
    try:
        rows = _fetch_events_for_range(conn, start_date, end_date)
    finally:
        conn.close()

    grouped = _group_events_by_trade(rows)
    all_trades: List[Dict[str, Any]] = []

    for trade_id, events in grouped.items():
        state = build_trade_state(events)
        if not state:
            continue
        if not _apply_filters(state, session, direction, status):
            continue

        # PHASE 7.A: Flatten for table list with telemetry-rich fields
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
            "time_et": time_et_str,
            "direction": state["direction"],
            "session": state["session"],
            "status": state["status"],
            "entry_price": state["entry_price"],
            "stop_loss": state["stop_loss"],
            "risk_distance": state["risk_distance"],
            "be_mfe_R": state["be_mfe_R"],
            "no_be_mfe_R": state["no_be_mfe_R"],
            "final_mfe_R": state["final_mfe_R"],
            "last_event_time": state["last_event_time"],
            # PHASE 7.A: Nested telemetry objects
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
            "exit_reason": state.get("completed_reason")
        })

    calendar = build_calendar_view(all_trades)

    return {
        "calendar": calendar,
        "trades": all_trades,
    }


def get_trade_detail(trade_id: str) -> Optional[Dict[str, Any]]:
    """Return full trade detail + event timeline for a single trade_id.
    Used by the Trade Journey modal.
    PHASE 7.A: Enhanced with telemetry-rich setup, market_state, and targets."""
    conn = _get_db_conn()
    try:
        sql = """
        SELECT
            id,
            trade_id,
            event_type,
            direction,
            entry_price,
            stop_loss,
            session,
            bias,
            risk_distance,
            current_price,
            mfe,
            exit_price,
            final_mfe,
            timestamp,
            signal_date,
            signal_time,
            be_mfe,
            no_be_mfe
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC, id ASC
        """
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, [trade_id])
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        return None

    state = build_trade_state(rows)
    if not state:
        return None

    # PHASE 7.A: Extract entry and exit rows for telemetry
    entry_row = None
    exit_row = None
    for row in rows:
        if row["event_type"] == "ENTRY" and entry_row is None:
            entry_row = row
        if row["event_type"] in ("EXIT_STOP_LOSS", "EXIT_BREAK_EVEN", "EXIT_TAKE_PROFIT", "EXIT_PARTIAL"):
            exit_row = row  # Keep last exit event

    # Extract telemetry from entry row
    market_state_entry = None
    targets_detail = None
    if entry_row and entry_row.get("telemetry"):
        entry_telemetry = entry_row["telemetry"]
        market_state_entry = entry_telemetry.get("market_state")
        targets_detail = entry_telemetry.get("targets")

    # Build event timeline for chart + log with telemetry-aware MFE
    events_timeline: List[Dict[str, Any]] = []
    for row in rows:
        telemetry = row.get("telemetry")
        
        # Prefer telemetry MFE values if available
        if telemetry:
            mfe_R = telemetry.get("mfe_R")
            mae_R = telemetry.get("mae_R")
        else:
            mfe_R = _decimal_to_float(row.get("mfe"))
            mae_R = None
        
        events_timeline.append({
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "event_type": row["event_type"],
            "be_mfe_R": _decimal_to_float(row.get("be_mfe")),
            "no_be_mfe_R": _decimal_to_float(row.get("no_be_mfe")),
            "mfe_R": mfe_R,
            "mae_R": mae_R,
            "current_price": _decimal_to_float(row.get("current_price")),
            "exit_price": _decimal_to_float(row.get("exit_price")),
        })

    # PHASE 7.A: Build detail with nested telemetry objects
    detail = {
        **state,
        "setup": {
            "family": state.get("setup_family"),
            "variant": state.get("setup_variant"),
            "id": state.get("setup_id"),
            "signal_strength": state.get("setup_strength")
        },
        "market_state_entry": market_state_entry,
        "targets": targets_detail or state.get("targets"),
        "events": events_timeline,
    }
    return detail


# ============================================================
# TRADE INTEGRITY ENGINE — PHASE 1 (backend only)
# ============================================================

def check_trade_integrity(events, state):
    """
    Return a dict with 8 categories of integrity checks.
    Each category is:
        { "ok": True/False, "reasons": [list of str] }
    """
    results = {
        "signal":         {"ok": True, "reasons": []},
        "lifecycle":      {"ok": True, "reasons": []},
        "mfe_updates":    {"ok": True, "reasons": []},
        "be_strategy":    {"ok": True, "reasons": []},
        "no_be_strategy": {"ok": True, "reasons": []},
        "mae":            {"ok": True, "reasons": []},
        "timestamps":     {"ok": True, "reasons": []},
        "telemetry":      {"ok": True, "reasons": []},
    }
    
    # --------------------
    # Helper accessors
    # --------------------
    types = [e.get("event_type") for e in events]
    entry_events = [e for e in events if e.get("event_type") == "ENTRY"]
    exit_events  = [e for e in events if e.get("event_type") in ("EXIT_STOP_LOSS","EXIT_BREAK_EVEN","EXIT_SL","EXIT_BE")]
    mfe_updates  = [e for e in events if e.get("event_type") == "MFE_UPDATE"]
    
    # Quick helpers
    def fail(cat, msg):
        results[cat]["ok"] = False
        results[cat]["reasons"].append(msg)
    
    # Extract timestamps
    ts_list = [e.get("timestamp") for e in events if e.get("timestamp")]
    
    # ============================================================
    # CATEGORY 1: SIGNAL INTEGRITY
    # ============================================================
    sig_date = state.get("signal_date")
    sig_time = state.get("signal_time")
    if not sig_date or not sig_time:
        fail("signal", "Missing signal_date or signal_time.")
    
    # Signal vs entry time consistency (if available)
    try:
        from datetime import datetime
        import pytz
        if sig_date and sig_time and events:
            signal_dt = datetime.fromisoformat(f"{sig_date}T{sig_time}")
            first_ts = events[0]["timestamp"]
            if first_ts:
                diff_sec = abs((signal_dt - first_ts).total_seconds())
                if diff_sec > 300:  # > 5 minutes difference
                    fail("signal", f"Signal time differs from first event by {diff_sec:.1f}s.")
    except:
        pass
    
    # ============================================================
    # CATEGORY 2: LIFECYCLE
    # ============================================================
    if len(entry_events) != 1:
        fail("lifecycle", f"Expected exactly 1 ENTRY event, found {len(entry_events)}.")
    
    if exit_events and not entry_events:
        fail("lifecycle", "EXIT event present without ENTRY.")
    
    # ORDER CHECK
    if entry_events and exit_events:
        if exit_events[0]["timestamp"] < entry_events[0]["timestamp"]:
            fail("lifecycle", "EXIT timestamp precedes ENTRY timestamp.")
    
    # ============================================================
    # CATEGORY 3: MFE UPDATES (GENERAL)
    # ============================================================
    if entry_events and exit_events:
        if len(mfe_updates) == 0:
            fail("mfe_updates", "Completed trade has no MFE_UPDATE events.")
    
    # ============================================================
    # CATEGORY 4: BE STRATEGY INTEGRITY
    # ============================================================
    be_vals = [e.get("be_mfe") for e in events if e.get("be_mfe") is not None]
    be_triggered = any(e.get("event_type") == "BE_TRIGGERED" for e in events)
    
    # BE MFE never moves
    if len(be_vals) > 0:
        if max(be_vals) == min(be_vals) == 0:
            fail("be_strategy", "BE MFE never moves from 0.")
    
    # Missing BE_TRIGGERED when No-BE >= 1R
    nobe_vals = [e.get("no_be_mfe") for e in events if e.get("no_be_mfe") is not None]
    if nobe_vals and max(nobe_vals) >= 1.0 and not be_triggered:
        fail("be_strategy", "No BE_TRIGGERED event despite No-BE MFE >= 1R.")
    
    # BE exit must be final_mfe == 0 for BE leg (if present)
    if exit_events:
        if exit_events[0].get("event_type") in ("EXIT_BE","EXIT_BREAK_EVEN"):
            if state.get("final_mfe_R") not in (0, 0.0, None):
                fail("be_strategy", f"BE exit final_mfe_R expected 0, got {state.get('final_mfe_R')}.")
    
    # ============================================================
    # CATEGORY 5: NO-BE STRATEGY INTEGRITY
    # ============================================================
    if entry_events and exit_events:
        if len(nobe_vals) == 0:
            fail("no_be_strategy", "No No-BE MFE values recorded for completed trade.")
        else:
            if max(nobe_vals) == 0:
                fail("no_be_strategy", "No-BE MFE never moves from 0.")
    
    # ============================================================
    # CATEGORY 6: MAE INTEGRITY
    # ============================================================
    mae_vals = [e.get("mae_R") or e.get("mae_global_r") for e in events 
                if (e.get("mae_R") or e.get("mae_global_r") is not None)]
    
    if entry_events and exit_events:
        if len(mae_vals) == 0:
            fail("mae", "No MAE recorded for completed trade.")
    
    # Polarity
    for mv in mae_vals:
        try:
            if mv is not None and float(mv) > 0:
                fail("mae", "MAE polarity violation (MAE > 0).")
        except:
            pass
    
    # ============================================================
    # CATEGORY 7: TIMESTAMP CONSISTENCY
    # ============================================================
    # Monotonic check
    for i in range(1, len(ts_list)):
        if ts_list[i] < ts_list[i-1]:
            fail("timestamps", "Non-monotonic timestamps detected.")
    
    # ============================================================
    # CATEGORY 8: TELEMETRY INTEGRITY
    # ============================================================
    # Required fields
    required_fields = ["entry_price","stop_loss","risk_distance"]
    for f in required_fields:
        if state.get(f) in (None, 0, 0.0):
            fail("telemetry", f"Missing or zero telemetry field: {f}.")
    
    return results


def build_integrity_report_for_trade(events, state):
    """
    Build unified integrity payload with:
    - category results
    - a flattened list of all failure reasons
    """
    results = check_trade_integrity(events, state)
    
    all_failures = []
    for cat, r in results.items():
        if not r["ok"]:
            for msg in r["reasons"]:
                all_failures.append(f"{cat}: {msg}")
    
    return {
        "categories": results,
        "all_failures": all_failures,
        "healthy": len(all_failures) == 0
    }


def recover_missing_entry_timestamps(events_list):
    """
    Repairs ENTRY rows missing signal_date or signal_time.
    Uses the earliest available event_timestamp from MFE_UPDATE,
    BE_TRIGGERED, EXIT_BE, or EXIT_SL events in raw_payload.
    
    Returns tuple:
        (needs_update: bool, recovered_date: date or None, recovered_time: time or None)
    """
    import json
    from dateutil import parser as date_parser
    
    # Filter ENTRY event
    entry = None
    for ev in events_list:
        if ev.get("event_type") == "ENTRY":
            entry = ev
            break
    
    if not entry:
        return (False, None, None)
    
    if entry.get("signal_date") and entry.get("signal_time"):
        return (False, None, None)
    
    # Find earliest downstream event with valid timestamp
    candidate_ts = None
    for ev in events_list:
        if ev.get("event_type") in ("MFE_UPDATE", "BE_TRIGGERED", "EXIT_BE", "EXIT_SL"):
            raw = ev.get("raw_payload")
            if not raw:
                continue
            try:
                payload = json.loads(raw)
                ts = payload.get("event_timestamp")
                if ts:
                    parsed = date_parser.parse(ts)
                    if candidate_ts is None or parsed < candidate_ts:
                        candidate_ts = parsed
            except:
                continue
    
    if not candidate_ts:
        return (False, None, None)
    
    return (
        True,
        candidate_ts.date(),
        candidate_ts.time().replace(microsecond=0)
    )


def recover_missing_mae(events):
    """
    Repairs missing MAE (Maximum Adverse Excursion) for completed trades.
    Scans MFE_UPDATE events for mae_global_r values and finds the worst (most negative).
    
    Returns tuple:
        (needs_update: bool, old_mae: float or None, new_mae: float or None)
    """
    # Check if trade has EXIT event
    has_exit = any(e.get("event_type") in ("EXIT_BE", "EXIT_SL", "EXIT_STOP_LOSS", "EXIT_BREAK_EVEN") 
                   for e in events)
    if not has_exit:
        return (False, None, None)
    
    # Get current MAE from EXIT event
    exit_event = None
    for e in events:
        if e.get("event_type") in ("EXIT_BE", "EXIT_SL", "EXIT_STOP_LOSS", "EXIT_BREAK_EVEN"):
            exit_event = e
            break
    
    if not exit_event:
        return (False, None, None)
    
    current_mae = exit_event.get("mae_global_r")
    
    # If MAE already exists and is non-zero, no update needed
    if current_mae is not None and current_mae != 0:
        return (False, current_mae, current_mae)
    
    # Scan MFE_UPDATE events for mae_global_r values
    mae_values = []
    for e in events:
        if e.get("event_type") == "MFE_UPDATE":
            mae = e.get("mae_global_r")
            if mae is not None:
                try:
                    mae_values.append(float(mae))
                except:
                    pass
    
    if not mae_values:
        return (False, current_mae, None)
    
    # MAE is the worst (most negative) adverse excursion
    worst_mae = min(mae_values)
    
    # Ensure MAE is never positive
    if worst_mae > 0:
        worst_mae = 0.0
    
    return (True, current_mae, worst_mae)


def repair_trade_lifecycle(events):
    """
    Repairs malformed lifecycle sequences.
    Ensures canonical ordering:
        ENTRY → MFE_UPDATE* → BE_TRIGGERED? → EXIT_(BE|SL|TP)
    Reconstructs missing ENTRY when possible.
    Fixes EXIT-before-ENTRY violations.
    Returns: (updated_events, changed_flag)
    """
    changed = False
    
    # Sort chronologically
    events = sorted(events, key=lambda e: e.get("timestamp") or 0)
    
    entry_events = [e for e in events if e["event_type"] == "ENTRY"]
    exit_events  = [e for e in events if e["event_type"].startswith("EXIT")]
    mfe_events   = [e for e in events if e["event_type"] == "MFE_UPDATE"]
    
    # 1) Reconstruct ENTRY if missing
    if not entry_events:
        first = events[0]
        reconstructed = {
            **first,
            "event_type": "ENTRY",
            "signal_date": first.get("signal_date"),
            "signal_time": first.get("signal_time"),
        }
        events.insert(0, reconstructed)
        changed = True
    
    # 2) Fix EXIT before ENTRY
    entry_ts = events[0].get("timestamp")
    for ex in exit_events:
        if ex.get("timestamp") and entry_ts and ex["timestamp"] < entry_ts:
            ex["timestamp"] = entry_ts  # move to entry timestamp
            changed = True
    
    # 3) Ensure BE_TRIGGERED exists when MFE >= BE threshold
    be_events = [e for e in events if e["event_type"] == "BE_TRIGGERED"]
    if not be_events:
        # Safely compute max MFE across lifecycle events, ignoring None / bad values
        mfe_raw = [e.get("mfe") for e in mfe_events]
        mfe_numeric = []
        for v in mfe_raw:
            if v is None:
                continue
            try:
                mfe_numeric.append(float(v))
            except (TypeError, ValueError):
                # Ignore non-numeric MFE values defensively
                continue
        max_mfe = max(mfe_numeric) if mfe_numeric else 0.0
        if max_mfe >= 1.0:
            derived = {
                "event_type": "BE_TRIGGERED",
                "timestamp": entry_ts,
                "be_mfe": max_mfe,
            }
            events.append(derived)
            changed = True
    
    # Re-sort after repairs
    events = sorted(events, key=lambda e: e.get("timestamp") or 0)
    
    return events, changed
