"""
Signal Contract V1 - Debug Endpoints
Read-only endpoints for verifying Wave 1 field population
"""

from flask import Blueprint, request, jsonify
import psycopg2
import os

signals_debug_v1_bp = Blueprint("signals_debug_v1_bp", __name__, url_prefix="/api/signals/v1/debug")

print("[BOOT] api.signals_debug_v1 loaded; signals_debug_v1_bp=", "OK" if 'signals_debug_v1_bp' in globals() else "MISSING")

def get_db_conn():
    """Get database connection"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@signals_debug_v1_bp.route('/last', methods=['GET'])
def get_last_events():
    """Get last N events with Wave 1 fields"""
    limit = min(int(request.args.get('limit', 20)), 100)
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, trade_id, event_type, direction, created_at,
            symbol, logic_version, source, status,
            signal_bar_open_ts, signal_bar_close_ts,
            confirmation_bar_open_ts, confirmation_bar_close_ts,
            entry_bar_open_ts, entry_bar_close_ts,
            exit_bar_open_ts, exit_bar_close_ts,
            signal_candle_high, signal_candle_low,
            entry_price, stop_loss, risk_distance,
            be_enabled, be_trigger_R, be_offset_points, be_triggered,
            be_trigger_bar_open_ts, be_trigger_bar_close_ts,
            highest_high, lowest_low, extremes_last_updated_bar_open_ts,
            mfe, be_mfe, no_be_mfe, mae_global_r
        FROM automated_signals
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    
    rows = cursor.fetchall()
    
    events = []
    for row in rows:
        event = {
            "id": row[0],
            "trade_id": row[1],
            "event_type": row[2],
            "direction": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "wave1_fields": {
                "symbol": row[5],
                "logic_version": row[6],
                "source": row[7],
                "status": row[8],
                "timestamps": {
                    "signal_bar_open_ts": row[9].isoformat() if row[9] else None,
                    "signal_bar_close_ts": row[10].isoformat() if row[10] else None,
                    "confirmation_bar_open_ts": row[11].isoformat() if row[11] else None,
                    "confirmation_bar_close_ts": row[12].isoformat() if row[12] else None,
                    "entry_bar_open_ts": row[13].isoformat() if row[13] else None,
                    "entry_bar_close_ts": row[14].isoformat() if row[14] else None,
                    "exit_bar_open_ts": row[15].isoformat() if row[15] else None,
                    "exit_bar_close_ts": row[16].isoformat() if row[16] else None
                },
                "signal_candle": {
                    "high": float(row[17]) if row[17] else None,
                    "low": float(row[18]) if row[18] else None
                },
                "entry_stop": {
                    "entry_price": float(row[19]) if row[19] else None,
                    "stop_loss": float(row[20]) if row[20] else None,
                    "risk_distance": float(row[21]) if row[21] else None
                },
                "breakeven": {
                    "be_enabled": row[22],
                    "be_trigger_R": float(row[23]) if row[23] else None,
                    "be_offset_points": float(row[24]) if row[24] else None,
                    "be_triggered": row[25],
                    "be_trigger_bar_open_ts": row[26].isoformat() if row[26] else None,
                    "be_trigger_bar_close_ts": row[27].isoformat() if row[27] else None
                },
                "extremes": {
                    "highest_high": float(row[28]) if row[28] else None,
                    "lowest_low": float(row[29]) if row[29] else None,
                    "extremes_last_updated_bar_open_ts": row[30].isoformat() if row[30] else None
                },
                "mfe_metrics": {
                    "mfe": float(row[31]) if row[31] else None,
                    "be_mfe": float(row[32]) if row[32] else None,
                    "no_be_mfe": float(row[33]) if row[33] else None,
                    "mae_global_r": float(row[34]) if row[34] else None
                }
            }
        }
        events.append(event)
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "count": len(events),
        "limit": limit,
        "events": events
    })

@signals_debug_v1_bp.route('/trade/<trade_id>', methods=['GET'])
def get_trade_timeline(trade_id):
    """Get complete event timeline for a trade_id with Wave 1 fields"""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, event_type, direction, created_at,
            symbol, logic_version, source, status,
            signal_bar_open_ts, signal_bar_close_ts,
            confirmation_bar_open_ts, confirmation_bar_close_ts,
            entry_bar_open_ts, entry_bar_close_ts,
            exit_bar_open_ts, exit_bar_close_ts,
            signal_candle_high, signal_candle_low,
            entry_price, stop_loss, risk_distance,
            be_enabled, be_trigger_R, be_offset_points, be_triggered,
            be_trigger_bar_open_ts, be_trigger_bar_close_ts,
            highest_high, lowest_low, extremes_last_updated_bar_open_ts,
            mfe, be_mfe, no_be_mfe, mae_global_r,
            session, bias, current_price, exit_price, final_mfe
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY created_at ASC
    """, (trade_id,))
    
    rows = cursor.fetchall()
    
    if not rows:
        cursor.close()
        conn.close()
        return jsonify({"error": "trade_id not found"}), 404
    
    events = []
    for row in rows:
        event = {
            "id": row[0],
            "event_type": row[1],
            "direction": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "wave1_fields": {
                "symbol": row[4],
                "logic_version": row[5],
                "source": row[6],
                "status": row[7],
                "timestamps": {
                    "signal_bar_open_ts": row[8].isoformat() if row[8] else None,
                    "signal_bar_close_ts": row[9].isoformat() if row[9] else None,
                    "confirmation_bar_open_ts": row[10].isoformat() if row[10] else None,
                    "confirmation_bar_close_ts": row[11].isoformat() if row[11] else None,
                    "entry_bar_open_ts": row[12].isoformat() if row[12] else None,
                    "entry_bar_close_ts": row[13].isoformat() if row[13] else None,
                    "exit_bar_open_ts": row[14].isoformat() if row[14] else None,
                    "exit_bar_close_ts": row[15].isoformat() if row[15] else None
                },
                "signal_candle": {
                    "high": float(row[16]) if row[16] else None,
                    "low": float(row[17]) if row[17] else None
                },
                "entry_stop": {
                    "entry_price": float(row[18]) if row[18] else None,
                    "stop_loss": float(row[19]) if row[19] else None,
                    "risk_distance": float(row[20]) if row[20] else None
                },
                "breakeven": {
                    "be_enabled": row[21],
                    "be_trigger_R": float(row[22]) if row[22] else None,
                    "be_offset_points": float(row[23]) if row[23] else None,
                    "be_triggered": row[24],
                    "be_trigger_bar_open_ts": row[25].isoformat() if row[25] else None,
                    "be_trigger_bar_close_ts": row[26].isoformat() if row[26] else None
                },
                "extremes": {
                    "highest_high": float(row[27]) if row[27] else None,
                    "lowest_low": float(row[28]) if row[28] else None,
                    "extremes_last_updated_bar_open_ts": row[29].isoformat() if row[29] else None
                },
                "mfe_metrics": {
                    "mfe": float(row[30]) if row[30] else None,
                    "be_mfe": float(row[31]) if row[31] else None,
                    "no_be_mfe": float(row[32]) if row[32] else None,
                    "mae_global_r": float(row[33]) if row[33] else None
                }
            },
            "legacy_fields": {
                "session": row[34],
                "bias": row[35],
                "current_price": float(row[36]) if row[36] else None,
                "exit_price": float(row[37]) if row[37] else None,
                "final_mfe": float(row[38]) if row[38] else None
            }
        }
        events.append(event)
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "trade_id": trade_id,
        "event_count": len(events),
        "events": events
    })
