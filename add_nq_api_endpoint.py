#!/usr/bin/env python3
"""
Add NQ OHLCV-1M stats API endpoint to web_server.py
"""

# The endpoint code to add
endpoint_code = '''
@app.route('/api/market-data/nq/ohlcv-1m/stats', methods=['GET'])
def nq_ohlcv_1m_stats():
    """
    Get NQ OHLCV-1M dataset statistics (15 years: 2010-2025)
    
    Returns:
        JSON with row count, date range, and latest bar info
    """
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not configured'}), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as row_count,
                MIN(ts) as min_ts,
                MAX(ts) as max_ts,
                (SELECT close FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'GLBX.MDP3:NQ' 
                 ORDER BY ts DESC LIMIT 1) as latest_close,
                (SELECT ts FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'GLBX.MDP3:NQ' 
                 ORDER BY ts DESC LIMIT 1) as latest_ts
            FROM market_bars_ohlcv_1m
            WHERE symbol = 'GLBX.MDP3:NQ'
        """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] > 0:
            return jsonify({
                'row_count': result[0],
                'min_ts': result[1].isoformat() if result[1] else None,
                'max_ts': result[2].isoformat() if result[2] else None,
                'latest_close': float(result[3]) if result[3] else None,
                'latest_ts': result[4].isoformat() if result[4] else None,
                'symbol': 'GLBX.MDP3:NQ',
                'timeframe': '1m',
                'vendor': 'databento',
                'years': round((result[2] - result[1]).days / 365.25, 1) if result[1] and result[2] else None
            })
        else:
            return jsonify({
                'row_count': 0,
                'message': 'No NQ data ingested yet',
                'symbol': 'GLBX.MDP3:NQ',
                'timeframe': '1m',
                'vendor': 'databento'
            })
            
    except Exception as e:
        logger.exception("[NQ_STATS_ERROR]")
        return jsonify({'error': str(e)}), 500
'''

print("=" * 80)
print("NQ API ENDPOINT CODE")
print("=" * 80)
print("\nAdd this endpoint to web_server.py (after the MNQ endpoint):\n")
print(endpoint_code)
print("\n" + "=" * 80)
print("MANUAL STEPS:")
print("=" * 80)
print("1. Open web_server.py")
print("2. Find the MNQ endpoint: @app.route('/api/market-data/mnq/ohlcv-1m/stats')")
print("3. Add the NQ endpoint code above after it")
print("4. Save the file")
print("5. Verify with: git status web_server.py")
print("6. Commit and push to deploy")
print("=" * 80)
