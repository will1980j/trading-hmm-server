from flask import Blueprint, request, jsonify
import psycopg2, os

signals_debug_v1_bp = Blueprint("signals_debug_v1_bp", __name__, url_prefix="/api/signals/v1/debug")
print("[BOOT] api.signals_debug_v1 loaded OK")

def get_db_conn():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@signals_debug_v1_bp.route('/last', methods=['GET'])
def get_last_events():
    limit = min(int(request.args.get('limit', 20)), 100)
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, trade_id, event_type, direction, timestamp, symbol, logic_version, source, status, signal_bar_open_ts, entry_bar_open_ts, exit_bar_open_ts, signal_candle_high, signal_candle_low, entry_price, stop_loss, be_enabled, be_triggered, be_trigger_bar_open_ts, highest_high, lowest_low, mfe, be_mfe, no_be_mfe, mae_global_r FROM automated_signals ORDER BY id DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    events = [{"id": r[0], "trade_id": r[1], "event_type": r[2], "direction": r[3], "timestamp": r[4].isoformat() if r[4] else None, "wave1": {"symbol": r[5], "logic_version": r[6], "source": r[7], "status": r[8], "signal_bar_open_ts": r[9].isoformat() if r[9] else None, "entry_bar_open_ts": r[10].isoformat() if r[10] else None, "exit_bar_open_ts": r[11].isoformat() if r[11] else None, "signal_candle_high": float(r[12]) if r[12] else None, "signal_candle_low": float(r[13]) if r[13] else None, "entry_price": float(r[14]) if r[14] else None, "stop_loss": float(r[15]) if r[15] else None, "be_enabled": r[16], "be_triggered": r[17], "be_trigger_bar_open_ts": r[18].isoformat() if r[18] else None, "highest_high": float(r[19]) if r[19] else None, "lowest_low": float(r[20]) if r[20] else None, "mfe": float(r[21]) if r[21] else None, "be_mfe": float(r[22]) if r[22] else None, "no_be_mfe": float(r[23]) if r[23] else None, "mae_global_r": float(r[24]) if r[24] else None}} for r in rows]
    cursor.close()
    conn.close()
    return jsonify({"count": len(events), "limit": limit, "events": events})

@signals_debug_v1_bp.route('/trade/<trade_id>', methods=['GET'])
def get_trade_timeline(trade_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_type, direction, timestamp, symbol, logic_version, source, status, signal_bar_open_ts, entry_bar_open_ts, exit_bar_open_ts, signal_candle_high, signal_candle_low, entry_price, stop_loss, be_enabled, be_triggered, be_trigger_bar_open_ts, highest_high, lowest_low, mfe, be_mfe, no_be_mfe, mae_global_r, session, bias FROM automated_signals WHERE trade_id = %s ORDER BY id ASC", (trade_id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.close()
        conn.close()
        return jsonify({"error": "trade_id not found"}), 404
    events = [{"id": r[0], "event_type": r[1], "direction": r[2], "timestamp": r[3].isoformat() if r[3] else None, "wave1": {"symbol": r[4], "logic_version": r[5], "source": r[6], "status": r[7], "signal_bar_open_ts": r[8].isoformat() if r[8] else None, "entry_bar_open_ts": r[9].isoformat() if r[9] else None, "exit_bar_open_ts": r[10].isoformat() if r[10] else None, "signal_candle_high": float(r[11]) if r[11] else None, "signal_candle_low": float(r[12]) if r[12] else None, "entry_price": float(r[13]) if r[13] else None, "stop_loss": float(r[14]) if r[14] else None, "be_enabled": r[15], "be_triggered": r[16], "be_trigger_bar_open_ts": r[17].isoformat() if r[17] else None, "highest_high": float(r[18]) if r[18] else None, "lowest_low": float(r[19]) if r[19] else None, "mfe": float(r[20]) if r[20] else None, "be_mfe": float(r[21]) if r[21] else None, "no_be_mfe": float(r[22]) if r[22] else None, "mae_global_r": float(r[23]) if r[23] else None}, "legacy": {"session": r[24], "bias": r[25]}} for r in rows]
    cursor.close()
    conn.close()
    return jsonify({"trade_id": trade_id, "event_count": len(events), "events": events})
