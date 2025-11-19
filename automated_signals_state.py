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
    `events` MUST already be sorted by timestamp ascending."""
    if not events:
        return None

    # Core identity from first event
    first = events[0]
    trade_id = first["trade_id"]
    direction = first["direction"]
    session = first["session"]
    bias = first.get("bias")
    entry_price = _decimal_to_float(first.get("entry_price"))
    stop_loss = _decimal_to_float(first.get("stop_loss"))
    risk_distance = _decimal_to_float(first.get("risk_distance"))
    targets = first.get("targets")  # leave JSON/dict/None as-is

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

        elif etype in ("EXIT_SL", "EXIT_BE", "EXIT_TP", "EXIT_TARGET", "SIGNAL_COMPLETED"):
            status = "COMPLETED"
            completed_reason = etype
            ep = row.get("exit_price") or row.get("current_price")
            if ep is not None:
                exit_price = _decimal_to_float(ep)
            if row.get("final_mfe") is not None:
                final_mfe = _decimal_to_float(row["final_mfe"])
            else:
                # If no explicit final_mfe, fall back to latest No-BE MFE, then BE MFE
                final_mfe = current_no_be_mfe if current_no_be_mfe is not None else current_be_mfe

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
    }
    return trade_state


# --- Hub data builders ------------------------------------------------------

def _fetch_events_for_range(
    conn,
    start_date: Optional[str],
    end_date: Optional[str],
) -> List[Dict[str, Any]]:
    """Fetch all automated_signals rows within [start_date, end_date].
    Dates are inclusive; if None, the range is unbounded on that side."""
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
        grouped[row["trade_id"]].append(row)
    return grouped


def build_calendar_view(trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate trades into calendar-style stats per signal_date."""
    by_date: Dict[str, Dict[str, Any]] = {}
    for trade in trades:
        date_key = trade["signal_date"]
        if date_key is None:
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

        # Flatten for table list
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
        })

    calendar = build_calendar_view(all_trades)

    return {
        "calendar": calendar,
        "trades": all_trades,
    }


def get_trade_detail(trade_id: str) -> Optional[Dict[str, Any]]:
    """Return full trade detail + event timeline for a single trade_id.
    Used by the Trade Journey modal."""
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

    # Build event timeline for chart + log
    events_timeline: List[Dict[str, Any]] = []
    for row in rows:
        events_timeline.append({
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "event_type": row["event_type"],
            "be_mfe_R": _decimal_to_float(row.get("be_mfe")),
            "no_be_mfe_R": _decimal_to_float(row.get("no_be_mfe")),
            "mfe_R": _decimal_to_float(row.get("mfe")),
            "current_price": _decimal_to_float(row.get("current_price")),
            "exit_price": _decimal_to_float(row.get("exit_price")),
        })

    detail = {
        **state,
        "events": events_timeline,
    }
    return detail
