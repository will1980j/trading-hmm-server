from flask import Blueprint, request, jsonify
import psycopg2, os

signals_v1_bp = Blueprint("signals_v1_bp", __name__, url_prefix="/api/signals/v1")
print("[BOOT] api.signals_v1 loaded OK")

def get_db_conn():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def normalize_status(status, event_type):
    if status in ['PENDING', 'CONFIRMED', 'EXITED', 'CANCELLED']:
        return status
    if status == 'ACTIVE':
        return 'CONFIRMED'
    if status == 'COMPLETED':
        return 'EXITED'
    if status is None:
        if event_type == 'SIGNAL_CREATED':
            return 'PENDING'
        elif event_type in ['ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED']:
            return 'CONFIRMED'
        elif event_type and event_type.startswith('EXIT'):
            return 'EXITED'
        elif event_type == 'CANCELLED':
            return 'CANCELLED'
    return status

def normalize_direction(direction):
    if direction in ['Bullish', 'Bearish']:
        return direction, direction
    if direction == 'LONG':
        return 'LONG', 'Bullish'
    if direction == 'SHORT':
        return 'SHORT', 'Bearish'
    return direction, direction

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
        SELECT DISTINCT ON (trade_id)
            trade_id, symbol, status, direction, event_type, id,
            signal_bar_open_ts, entry_bar_open_ts, exit_bar_open_ts,
            entry_price, stop_loss, mfe, no_be_mfe, be_mfe, mae_global_r,
            timestamp
        FROM automated_signals
        ORDER BY trade_id, id DESC
    """
    
    if status_list:
        filter_query = f"""
            SELECT * FROM ({base_query}) latest
            WHERE symbol = %s AND status = ANY(%s)
            ORDER BY COALESCE(signal_bar_open_ts, entry_bar_open_ts, exit_bar_open_ts, timestamp) DESC NULLS LAST, id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(filter_query, (symbol, status_list, limit, offset))
    else:
        filter_query = f"""
            SELECT * FROM ({base_query}) latest
            WHERE symbol = %s
            ORDER BY COALESCE(signal_bar_open_ts, entry_bar_open_ts, exit_bar_open_ts, timestamp) DESC NULLS LAST, id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(filter_query, (symbol, limit, offset))
    
    rows = cursor.fetchall()
    
    result_rows = []
    for r in rows:
        status_norm = normalize_status(r[2], r[4])
        direction_raw, direction_norm = normalize_direction(r[3])
        
        result_rows.append({
            "trade_id": r[0],
            "symbol": r[1],
            "status": status_norm,
            "direction": direction_raw,
            "direction_norm": direction_norm,
            "event_type": r[4],
            "event_id": r[5],
            "signal_bar_open_ts": r[6].isoformat() if r[6] else None,
            "entry_bar_open_ts": r[7].isoformat() if r[7] else None,
            "exit_bar_open_ts": r[8].isoformat() if r[8] else None,
            "entry_price": float(r[9]) if r[9] else None,
            "stop_loss": float(r[10]) if r[10] else None,
            "mfe": float(r[11]) if r[11] else None,
            "no_be_mfe": float(r[12]) if r[12] else None,
            "be_mfe": float(r[13]) if r[13] else None,
            "mae_global_r": float(r[14]) if r[14] else None
        })
    
    cursor.close()
    conn.close()
    
    return jsonify({"count": len(result_rows), "rows": result_rows})
