#!/usr/bin/env python3
"""
Add new endpoint to web_server.py that serves unified data
"""

endpoint_code = '''
@app.route('/api/trades-unified')
@login_required
def get_trades_unified():
    """Unified trades endpoint that matches signal lab data"""
    try:
        if not db_enabled or not db:
            return jsonify({"trades": [], "error": "Database not available"})
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id, date, time, bias, session, signal_type, 
                   COALESCE(mfe_none, mfe, 0) as mfe_none, created_at
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = false
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        trades = [{
            'id': row['id'],
            'date': str(row['date']),
            'time': str(row['time']),
            'bias': row['bias'],
            'session': row['session'],
            'signal_type': row['signal_type'],
            'mfe_none': float(row['mfe_none']) if row['mfe_none'] else 0,
            'created_at': str(row['created_at'])
        } for row in cursor.fetchall()]
        
        return jsonify({"trades": trades})
        
    except Exception as e:
        return jsonify({"trades": [], "error": str(e)[:200]}), 500
'''

print("Add this endpoint to web_server.py:")
print(endpoint_code)
print("\nThen update the frontend to use /api/trades-unified instead of /api/trades")