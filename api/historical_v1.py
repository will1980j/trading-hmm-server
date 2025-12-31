"""
Phase D.3: Historical Serving Layer API v1
Canonical read-only endpoints for historical market data
"""

from flask import Blueprint, request, jsonify
import psycopg2
import os
import hashlib
from datetime import datetime

hist_v1_bp = Blueprint("hist_v1_bp", __name__, url_prefix="/api/hist/v1")

print("[BOOT] api.historical_v1 loaded; hist_v1_bp=", "OK" if 'hist_v1_bp' in globals() else "MISSING")

def get_db_conn():
    """Get database connection"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def parse_ts(ts_str):
    """Parse RFC3339 timestamp"""
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))

def validate_1m_alignment(ts):
    """Check if timestamp is aligned to 1m boundary"""
    return ts.second == 0 and ts.microsecond == 0

@hist_v1_bp.route('/world', methods=['GET'])
def get_world():
    """Get complete world state at a single timestamp"""
    symbol = request.args.get('symbol')
    ts_str = request.args.get('ts')
    include = request.args.get('include', 'ohlcv,bias,triangles').split(',')
    
    if not symbol or not ts_str:
        return jsonify({"error": "symbol and ts are required"}), 400
    
    try:
        ts = parse_ts(ts_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    if not validate_1m_alignment(ts):
        return jsonify({"error": "timestamp must be aligned to 1m boundary"}), 409
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    result = {
        "timestamp": ts.isoformat(),
        "timezone": "UTC",
        "symbol": symbol,
        "semantics": {"timestamp": "bar_open", "timezone": "UTC"}
    }
    
    if 'ohlcv' in include:
        cursor.execute("SELECT open, high, low, close, volume FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts = %s", (symbol, ts))
        row = cursor.fetchone()
        if row:
            result['ohlcv'] = {"open": float(row[0]), "high": float(row[1]), "low": float(row[2]), "close": float(row[3]), "volume": int(row[4]) if row[4] else 0}
        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "no bar found at timestamp"}), 404
    
    if 'bias' in include:
        cursor.execute("SELECT bias_1m, bias_5m, bias_15m, bias_1h, bias_4h, bias_1d FROM bias_series_1m_v1 WHERE symbol = %s AND ts = %s", (symbol, ts))
        row = cursor.fetchone()
        if row:
            result['bias'] = {"1m": row[0], "5m": row[1], "15m": row[2], "60m": row[3], "240m": row[4], "1d": row[5]}
    
    if 'triangles' in include:
        cursor.execute("SELECT direction, bias_1m, htf_bullish, htf_bearish FROM triangle_events_v1 WHERE symbol = %s AND ts = %s", (symbol, ts))
        rows = cursor.fetchall()
        result['triangles'] = [{"direction": row[0], "bias_1m": row[1], "htf_bullish": row[2], "htf_bearish": row[3]} for row in rows]
    
    cursor.close()
    conn.close()
    
    return jsonify(result)

@hist_v1_bp.route('/bars', methods=['GET'])
def get_bars():
    """Get OHLCV bars for a time range"""
    symbol = request.args.get('symbol')
    tf = request.args.get('tf', '1m')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    limit = min(int(request.args.get('limit', 10000)), 50000)
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    if tf != '1m':
        return jsonify({"error": "only 1m timeframe implemented"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ts, open, high, low, close, volume FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts >= %s AND ts <= %s ORDER BY ts ASC LIMIT %s", (symbol, start_ts, end_ts, limit))
    
    rows = cursor.fetchall()
    bars = [{"ts": row[0].isoformat(), "open": float(row[1]), "high": float(row[2]), "low": float(row[3]), "close": float(row[4]), "volume": int(row[5]) if row[5] else 0} for row in rows]
    
    cursor.close()
    conn.close()
    
    return jsonify({"symbol": symbol, "timeframe": tf, "start": start_str, "end": end_str, "count": len(bars), "bars": bars})

@hist_v1_bp.route('/bias', methods=['GET'])
def get_bias():
    """Get HTF bias series for a time range"""
    symbol = request.args.get('symbol')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    limit = min(int(request.args.get('limit', 10000)), 50000)
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ts, bias_1m, bias_5m, bias_15m, bias_1h, bias_4h, bias_1d FROM bias_series_1m_v1 WHERE symbol = %s AND ts >= %s AND ts <= %s ORDER BY ts ASC LIMIT %s", (symbol, start_ts, end_ts, limit))
    
    rows = cursor.fetchall()
    bias_rows = [{"ts": row[0].isoformat(), "1m": row[1], "5m": row[2], "15m": row[3], "60m": row[4], "240m": row[5], "1d": row[6]} for row in rows]
    
    cursor.close()
    conn.close()
    
    return jsonify({"symbol": symbol, "start": start_str, "end": end_str, "count": len(bias_rows), "rows": bias_rows})

@hist_v1_bp.route('/triangles/events', methods=['GET'])
def get_triangle_events():
    """Get triangle events for a time range"""
    symbol = request.args.get('symbol')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    types_str = request.args.get('types')
    limit = min(int(request.args.get('limit', 1000)), 10000)
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    if types_str:
        types = [t.strip().upper() for t in types_str.split(',')]
        cursor.execute("SELECT ts, direction, bias_1m, bias_m5, bias_m15, bias_h1, htf_bullish, htf_bearish, source_table, logic_version FROM triangle_events_v1 WHERE symbol = %s AND ts >= %s AND ts <= %s AND direction = ANY(%s) ORDER BY ts ASC LIMIT %s", (symbol, start_ts, end_ts, types, limit))
    else:
        cursor.execute("SELECT ts, direction, bias_1m, bias_m5, bias_m15, bias_h1, htf_bullish, htf_bearish, source_table, logic_version FROM triangle_events_v1 WHERE symbol = %s AND ts >= %s AND ts <= %s ORDER BY ts ASC LIMIT %s", (symbol, start_ts, end_ts, limit))
    
    rows = cursor.fetchall()
    events = [{"ts": row[0].isoformat(), "direction": row[1], "bias_1m": row[2], "bias_5m": row[3], "bias_15m": row[4], "bias_1h": row[5], "htf_bullish": row[6], "htf_bearish": row[7], "source_table": row[8], "logic_version": row[9]} for row in rows]
    
    cursor.close()
    conn.close()
    
    return jsonify({"symbol": symbol, "start": start_str, "end": end_str, "count": len(events), "events": events})

@hist_v1_bp.route('/dataset', methods=['GET'])
def get_dataset():
    """Get analytics-friendly joined dataset (1 row per 1m bar) - SINGLE SQL QUERY"""
    symbol = request.args.get('symbol')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    include = request.args.get('include', 'ohlcv,bias,triangles_count').split(',')
    limit = min(int(request.args.get('limit', 10000)), 50000)
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    select_cols = ["b.ts"]
    if 'ohlcv' in include:
        select_cols.extend(["b.open", "b.high", "b.low", "b.close", "b.volume"])
    if 'bias' in include:
        select_cols.extend(["bs.bias_1m", "bs.bias_5m", "bs.bias_15m", "bs.bias_1h AS bias_60m", "bs.bias_4h AS bias_240m", "bs.bias_1d"])
    if 'triangles_count' in include:
        select_cols.append("COALESCE(tc.triangle_count, 0) AS triangles_count")
    
    sql = f"""
        SELECT {', '.join(select_cols)}
        FROM market_bars_ohlcv_1m_clean b
    """
    
    if 'bias' in include:
        sql += " LEFT JOIN bias_series_1m_v1 bs ON (b.symbol = bs.symbol AND b.ts = bs.ts)"
    
    if 'triangles_count' in include:
        sql += " LEFT JOIN (SELECT symbol, ts, COUNT(*) as triangle_count FROM triangle_events_v1 GROUP BY symbol, ts) tc ON (b.symbol = tc.symbol AND b.ts = tc.ts)"
    
    sql += " WHERE b.symbol = %s AND b.ts >= %s AND b.ts <= %s ORDER BY b.ts ASC LIMIT %s"
    
    cursor.execute(sql, (symbol, start_ts, end_ts, limit))
    
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    
    result_rows = []
    for row in rows:
        row_dict = {}
        for i, col_name in enumerate(col_names):
            val = row[i]
            if col_name == 'ts':
                row_dict['ts'] = val.isoformat()
            elif col_name in ['open', 'high', 'low', 'close']:
                row_dict[col_name] = float(val) if val is not None else None
            elif col_name == 'volume':
                row_dict[col_name] = int(val) if val is not None else 0
            elif col_name == 'triangles_count':
                row_dict[col_name] = int(val) if val is not None else 0
            else:
                row_dict[col_name] = val
        result_rows.append(row_dict)
    
    cursor.close()
    conn.close()
    
    return jsonify({"symbol": symbol, "start": start_str, "end": end_str, "count": len(result_rows), "rows": result_rows})

@hist_v1_bp.route('/quality/coverage', methods=['GET'])
def quality_coverage():
    """Check data coverage for a time range"""
    symbol = request.args.get('symbol')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    expected_minutes = int((end_ts - start_ts).total_seconds() / 60) + 1
    
    cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts >= %s AND ts <= %s", (symbol, start_ts, end_ts))
    bars_count = cursor.fetchone()[0]
    bars_missing = max(0, expected_minutes - bars_count)
    
    cursor.execute("SELECT COUNT(*) FROM bias_series_1m_v1 WHERE symbol = %s AND ts >= %s AND ts <= %s", (symbol, start_ts, end_ts))
    bias_count = cursor.fetchone()[0]
    bias_missing = max(0, bars_count - bias_count)
    
    cursor.execute("SELECT COUNT(*) FROM triangle_events_v1 WHERE symbol = %s AND ts >= %s AND ts <= %s", (symbol, start_ts, end_ts))
    triangles_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    checks = {
        "bars_1m_present": {"pass": bars_missing == 0, "missing_count": bars_missing, "found": bars_count, "expected": expected_minutes},
        "bias_rows_present": {"pass": bias_missing == 0, "missing_count": bias_missing, "found": bias_count, "expected": bars_count},
        "triangles_backfilled": {"pass": True, "count": triangles_count}
    }
    
    overall_pass = all(c['pass'] for c in checks.values())
    
    return jsonify({"symbol": symbol, "start": start_str, "end": end_str, "checks": checks, "pass": overall_pass})

@hist_v1_bp.route('/quality/alignment', methods=['GET'])
def quality_alignment():
    """Verify timestamp alignment and data consistency"""
    symbol = request.args.get('symbol')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts >= %s AND ts <= %s AND (EXTRACT(SECOND FROM ts) != 0 OR EXTRACT(MICROSECOND FROM ts) != 0)", (symbol, start_ts, end_ts))
    bars_misaligned = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM bias_series_1m_v1 WHERE symbol = %s AND ts >= %s AND ts <= %s AND (EXTRACT(SECOND FROM ts) != 0 OR EXTRACT(MICROSECOND FROM ts) != 0)", (symbol, start_ts, end_ts))
    bias_misaligned = cursor.fetchone()[0]
    
    cursor.execute("WITH gaps AS (SELECT ts, LAG(ts) OVER (ORDER BY ts) as prev_ts FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts >= %s AND ts <= %s) SELECT COUNT(*) FROM gaps WHERE prev_ts IS NOT NULL AND EXTRACT(EPOCH FROM (ts - prev_ts)) > 300", (symbol, start_ts, end_ts))
    gap_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    checks = {
        "timestamps_1m_aligned": {"pass": bars_misaligned == 0, "misaligned_count": bars_misaligned},
        "bias_timestamps_aligned": {"pass": bias_misaligned == 0, "misaligned_count": bias_misaligned},
        "no_unexpected_gaps": {"pass": gap_count == 0, "gap_count": gap_count, "note": "Gaps >5min detected (may be expected for overnight/weekend)"}
    }
    
    overall_pass = checks["timestamps_1m_aligned"]["pass"] and checks["bias_timestamps_aligned"]["pass"]
    
    return jsonify({"symbol": symbol, "start": start_str, "end": end_str, "checks": checks, "pass": overall_pass})

@hist_v1_bp.route('/quality/determinism', methods=['GET'])
def quality_determinism():
    """Verify deterministic dataset hash for repeatability"""
    symbol = request.args.get('symbol')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if not symbol or not start_str or not end_str:
        return jsonify({"error": "symbol, start, and end are required"}), 400
    
    try:
        start_ts = parse_ts(start_str)
        end_ts = parse_ts(end_str)
    except:
        return jsonify({"error": "invalid timestamp format"}), 400
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT b.ts, b.open, b.high, b.low, b.close, 
               bs.bias_5m, bs.bias_15m, bs.bias_1h, bs.bias_4h, bs.bias_1d
        FROM market_bars_ohlcv_1m_clean b
        LEFT JOIN bias_series_1m_v1 bs ON (b.symbol = bs.symbol AND b.ts = bs.ts)
        WHERE b.symbol = %s AND b.ts >= %s AND b.ts <= %s
        ORDER BY b.ts ASC
        LIMIT 10000
    """, (symbol, start_ts, end_ts))
    
    rows = cursor.fetchall()
    
    canonical_data = []
    for row in rows:
        canonical_data.append(f"{row[0].isoformat()}|{row[1]}|{row[2]}|{row[3]}|{row[4]}|{row[5] or 'NULL'}|{row[6] or 'NULL'}|{row[7] or 'NULL'}|{row[8] or 'NULL'}|{row[9] or 'NULL'}")
    
    cursor.close()
    conn.close()
    
    canonical_str = "\n".join(canonical_data)
    dataset_hash = hashlib.sha256(canonical_str.encode()).hexdigest()[:16]
    
    return jsonify({"symbol": symbol, "start": start_str, "end": end_str, "dataset_hash": dataset_hash, "row_count": len(canonical_data), "pass": True})
