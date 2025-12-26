#!/usr/bin/env python3
"""Insert NQ API endpoint into web_server.py"""

# Read the file
with open('web_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The NQ endpoint code to insert
nq_endpoint = '''
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

# Find the MNQ endpoint and insert NQ endpoint after it
marker = "        return jsonify(stats), 200\n        \n    except Exception as e:\n        logger.error(f\"❌ Error fetching MNQ OHLCV stats: {e}\")"

if marker in content:
    # Find the end of the MNQ endpoint function
    mnq_end = content.find("        }), 500\n\n\nif __name__ == '__main__':")
    
    if mnq_end != -1:
        # Insert NQ endpoint before the if __name__ block
        new_content = content[:mnq_end + len("        }), 500\n")] + nq_endpoint + content[mnq_end + len("        }), 500\n"):]
        
        # Write back to file
        with open('web_server.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ NQ endpoint inserted into web_server.py")
        print("\nVerify with: git diff web_server.py")
    else:
        print("❌ Could not find insertion point (if __name__ block)")
else:
    print("❌ Could not find MNQ endpoint marker")
    print("\nManually add the endpoint after the MNQ endpoint")
