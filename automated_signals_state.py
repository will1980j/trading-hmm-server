# automated_signals_state.py
## Pure backend logic for the Automated Signals Hub.
# - Reads rows from the automated_signals table
# - Folds events into canonical trade state
# - Builds calendar + trade list views
## THIS MODULE MUST NEVER WRITE TO THE DATABASE.
# READ-ONLY ONLY.

import os
from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras


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
        direction = telemetry.get("direction") or first["direction"]
        session = telemetry.get("session") or first["session"]
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
        direction = first["direction"]
        session = first["session"]
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

    # Default status if nothing changed it
    if status == "UNKNOWN":
        status = "ACTIVE"

    # For calendar / summary stats, we want a "max_mfe" concept.
    # Use No-BE as primary because it reflects full excursion, backed up by BE MFE.
    max_mfe_for_stats = max_no_be_mfe
    if max_mfe_for_stats is None:
        max_mfe_for_stats = max_be_mfe

    # Grab signal_date (assumed same for all rows of a trade)
    signal_date = events[0].get("signal_date")
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
        targets,
        current_price,
        mfe,
        exit_price,
        final_mfe,
        timestamp,
        signal_date,
        signal_time,
        be_mfe,
        no_be_mfe,
        telemetry
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
        grouped[row["trade_id"]].append(row)
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
        all_trades.append({
            "trade_id": state["trade_id"],
            "date": state["signal_date"],
            "time_et": state["signal_time"],
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
            "targets": state.get("targets")
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
            targets,
            current_price,
            mfe,
            exit_price,
            final_mfe,
            timestamp,
            signal_date,
            signal_time,
            be_mfe,
            no_be_mfe,
            telemetry
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
