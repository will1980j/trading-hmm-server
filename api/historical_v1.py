from flask import Blueprint, request, jsonify
import psycopg2, os, hashlib
from datetime import datetime

hist_v1_bp = Blueprint('hist_v1', __name__, url_prefix='/api/hist/v1')
print("[BOOT] api.historical_v1 loaded OK")

def get_db_conn():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

@hist_v1_bp.route('/world')
def get_world():
    symbol, ts_str = request.args.get('symbol'), request.args.get('ts')
    if not symbol or not ts_str:
        return jsonify({"error": "symbol and ts required"}), 400
    ts = parse_ts(ts_str)
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT open, high, low, close FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts = %s", (symbol, ts))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return jsonify({"error": "no bar found"}), 404
    return jsonify({"timestamp": ts.isoformat(), "symbol": symbol, "ohlcv": {"open": float(row[0]), "high": float(row[1]), "low": float(row[2]), "close": float(row[3])}})

@hist_v1_bp.route('/quality/coverage')
def quality_coverage():
    symbol, start_str, end_str = request.args.get('symbol'), request.args.get('start'), request.args.get('end')
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "required params missing"}), 400
    start_ts, end_ts = parse_ts(start_str), parse_ts(end_str)
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts >= %s AND ts <= %s", (symbol, start_ts, end_ts))
    bars_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"symbol": symbol, "checks": {"bars_1m_present": {"pass": bars_count > 0, "found": bars_count}}, "pass": bars_count > 0})
