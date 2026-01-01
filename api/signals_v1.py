from flask import Blueprint, request, jsonify
import psycopg2, os, logging

signals_v1_bp = Blueprint("signals_v1_bp", __name__, url_prefix="/api/signals/v1")
print("[BOOT] api.signals_v1 loaded OK")
logger = logging.getLogger(__name__)

def get_db_conn():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def normalize_direction(direction):
    if direction in ['Bullish', 'Bearish']:
        return direction
    if direction == 'LONG':
        return 'Bullish'
    if direction == 'SHORT':
        return 'Bearish'
    if direction and '_BULLISH' in str(direction).upper():
        return 'Bullish'
    if direction and '_BEARISH' in str(direction).upper():
        return 'Bearish'
    return direction

@signals_v1_bp.route('/all', methods=['GET'])
def get_all_signals():
    symbol = request.args.get('symbol', 'GLBX.MDP3:NQ')
    status_filter = request.args.get('status', '')
    limit = min(int(request.args.get('limit', 500)), 2000)
    offset = int(request.args.get('offset', 0))
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    status_list = [s.strip().upper() for s in status_filter.split(',') if s.strip()] if status_filter else []
    
    base_query = """
        WITH lifecycle_summary AS (
            SELECT 
                trade_id,
                MAX(symbol) FILTER (WHERE symbol IS NOT NULL) as symbol,
                MAX(id) as latest_event_id,
                (ARRAY_AGG(event_type ORDER BY id DESC))[1] as latest_event_type,
                (ARRAY_AGG(direction ORDER BY id DESC) FILTER (WHERE direction IS NOT NULL))[1] as direction,
                MIN(signal_bar_open_ts) FILTER (WHERE event_type='SIGNAL_CREATED' AND signal_bar_open_ts IS NOT NULL) as signal_bar_open_ts,
                MIN(entry_bar_open_ts) FILTER (WHERE event_type='ENTRY' AND entry_bar_open_ts IS NOT NULL) as entry_bar_open_ts,
                MAX(exit_bar_open_ts) FILTER (WHERE event_type LIKE 'EXIT%%' AND exit_bar_open_ts IS NOT NULL) as exit_bar_open_ts,
                (ARRAY_AGG(entry_price ORDER BY id DESC) FILTER (WHERE entry_price IS NOT NULL))[1] as entry_price,
                (ARRAY_AGG(stop_loss ORDER BY id DESC) FILTER (WHERE stop_loss IS NOT NULL))[1] as stop_loss,
                (ARRAY_AGG(no_be_mfe ORDER BY id DESC) FILTER (WHERE no_be_mfe IS NOT NULL))[1] as no_be_mfe,
                (ARRAY_AGG(be_mfe ORDER BY id DESC) FILTER (WHERE be_mfe IS NOT NULL))[1] as be_mfe,
                (ARRAY_AGG(mae_global_r ORDER BY id DESC) FILTER (WHERE mae_global_r IS NOT NULL))[1] as mae_global_r,
                MAX(timestamp) as latest_timestamp,
                CASE 
                    WHEN BOOL_OR(event_type = 'CANCELLED') THEN 'CANCELLED'
                    WHEN BOOL_OR(event_type LIKE 'EXIT%%') THEN 'EXITED'
                    WHEN BOOL_OR(event_type IN ('ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED')) THEN 'CONFIRMED'
                    ELSE 'PENDING'
                END as status
            FROM automated_signals
            GROUP BY trade_id
        )
        SELECT l.*, m.no_be_mfe as computed_no_be_mfe, m.be_mfe as computed_be_mfe, m.mae_global_r as computed_mae
        FROM lifecycle_summary l
        LEFT JOIN signal_metrics_v1 m ON l.trade_id = m.trade_id
        WHERE l.symbol = %(symbol)s
    """
    
    params = {"symbol": symbol, "limit": limit, "offset": offset}
    
    if status_list:
        base_query += " AND l.status = ANY(%(status_list)s)"
        params["status_list"] = status_list
    
    base_query += " ORDER BY COALESCE(l.signal_bar_open_ts, l.entry_bar_open_ts, l.exit_bar_open_ts, l.latest_timestamp) DESC NULLS LAST LIMIT %(limit)s OFFSET %(offset)s"
    
    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    
    # Batch check for bar existence
    all_ts = []
    for r in rows:
        if r[5]: all_ts.append(r[5])  # signal_bar_open_ts
        if r[6]: all_ts.append(r[6])  # entry_bar_open_ts
        if r[7]: all_ts.append(r[7])  # exit_bar_open_ts
    
    existing_ts = set()
    if all_ts:
        cursor.execute("SELECT ts FROM market_bars_ohlcv_1m_clean WHERE symbol = %(symbol)s AND ts = ANY(%(ts_list)s)", {"symbol": symbol, "ts_list": all_ts})
        existing_ts = {row[0] for row in cursor.fetchall()}
    
    result_rows = []
    for r in rows:
        direction_norm = normalize_direction(r[4])
        
        # Validity check
        required_ts = [t for t in [r[5], r[6], r[7]] if t is not None]
        valid = all(t in existing_ts for t in required_ts) if required_ts else True
        invalid_reason = None if valid else 'NO_BARS'
        
        # Coalesce metrics
        no_be_mfe = r[10] if r[10] is not None else r[15]
        be_mfe = r[11] if r[11] is not None else r[16]
        mae = r[12] if r[12] is not None else r[17]
        metrics_source = 'event' if r[10] is not None else ('computed' if r[15] is not None else 'missing')
        
        result_rows.append({
            "trade_id": r[0],
            "symbol": r[1],
            "status": r[14],
            "direction": r[4],
            "direction_norm": direction_norm,
            "signal_bar_open_ts": r[5].isoformat() if r[5] else None,
            "entry_bar_open_ts": r[6].isoformat() if r[6] else None,
            "exit_bar_open_ts": r[7].isoformat() if r[7] else None,
            "entry_price": float(r[8]) if r[8] else None,
            "stop_loss": float(r[9]) if r[9] else None,
            "no_be_mfe": float(no_be_mfe) if no_be_mfe else None,
            "be_mfe": float(be_mfe) if be_mfe else None,
            "mae_global_r": float(mae) if mae else None,
            "event_type": r[3],
            "event_id": r[2],
            "metrics_source": metrics_source,
            "valid_market_window": valid,
            "invalid_reason": invalid_reason
        })
    
    cursor.close()
    conn.close()
    
    return jsonify({"count": len(result_rows), "rows": result_rows})
