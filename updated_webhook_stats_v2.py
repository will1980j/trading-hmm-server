
@app.route('/api/webhook-stats', methods=['GET'])
@login_required
def get_webhook_stats():
    """Get webhook signal statistics - ENHANCED FOR V2"""
    try:
        if not db_enabled:
            return jsonify({'last_24h': [], 'last_bullish': None, 'last_bearish': None, 'total_signals': 0}), 200
        
        # Get fresh connection for this query
        from database.railway_db import RailwayDB
        query_db = RailwayDB(use_pool=True)
        
        if not query_db or not query_db.conn:
            return jsonify({'last_24h': [], 'last_bullish': None, 'last_bearish': None, 'total_signals': 0}), 200
        
        cursor = query_db.conn.cursor()
        
        # Get signal counts by bias in last 24 hours - COMBINED V1 + V2
        cursor.execute("""
            WITH combined_signals AS (
                -- V1 Signals
                SELECT bias, timestamp FROM live_signals
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                
                UNION ALL
                
                -- V2 Signals (convert bias format)
                SELECT 
                    CASE 
                        WHEN bias = 'bullish' THEN 'Bullish'
                        WHEN bias = 'bearish' THEN 'Bearish'
                        ELSE bias
                    END as bias,
                    signal_timestamp as timestamp
                FROM signal_lab_v2_trades
                WHERE signal_timestamp > NOW() - INTERVAL '24 hours'
            )
            SELECT bias, COUNT(*) as count
            FROM combined_signals
            GROUP BY bias
        """)
        last_24h = [dict(row) for row in cursor.fetchall()]
        
        # Get TOTAL signal count (all time) for ML training samples
        # Include V1 + V2 + Signal Lab historical data
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM live_signals) +
                (SELECT COUNT(*) FROM signal_lab_v2_trades) +
                (SELECT COUNT(*) FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0) as total
        """)
        total_row = cursor.fetchone()
        total_signals = total_row['total'] if total_row else 0
        
        # Get last bullish signal - COMBINED V1 + V2
        cursor.execute("""
            WITH combined_bullish AS (
                -- V1 Bullish
                SELECT timestamp FROM live_signals WHERE bias = 'Bullish'
                
                UNION ALL
                
                -- V2 Bullish
                SELECT signal_timestamp as timestamp FROM signal_lab_v2_trades WHERE bias = 'bullish'
            )
            SELECT timestamp FROM combined_bullish
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        bullish_row = cursor.fetchone()
        last_bullish = bullish_row['timestamp'].isoformat() if bullish_row else None
        
        # Get last bearish signal - COMBINED V1 + V2
        cursor.execute("""
            WITH combined_bearish AS (
                -- V1 Bearish
                SELECT timestamp FROM live_signals WHERE bias = 'Bearish'
                
                UNION ALL
                
                -- V2 Bearish
                SELECT signal_timestamp as timestamp FROM signal_lab_v2_trades WHERE bias = 'bearish'
            )
            SELECT timestamp FROM combined_bearish
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        bearish_row = cursor.fetchone()
        last_bearish = bearish_row['timestamp'].isoformat() if bearish_row else None
        
        # V2 ENHANCEMENT: Get automation statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as v2_total,
                COUNT(CASE WHEN auto_populated = true THEN 1 END) as automated_count,
                COUNT(CASE WHEN trade_status = 'ACTIVE' THEN 1 END) as active_trades,
                AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe ELSE current_mfe END) as avg_mfe,
                COUNT(CASE WHEN breakeven_achieved = true THEN 1 END) as breakeven_count
            FROM signal_lab_v2_trades
            WHERE signal_timestamp > NOW() - INTERVAL '24 hours'
        """)
        v2_stats_row = cursor.fetchone()
        v2_stats = dict(v2_stats_row) if v2_stats_row else {}
        
        query_db.close()
        
        return jsonify({
            'last_24h': last_24h,
            'last_bullish': last_bullish,
            'last_bearish': last_bearish,
            'total_signals': total_signals,
            'v2_stats': v2_stats,  # NEW: V2 automation statistics
            'data_sources': ['live_signals', 'signal_lab_v2_trades', 'signal_lab_trades']  # NEW: Source tracking
        })
        
    except Exception as e:
        logger.error(f"Webhook stats error: {str(e)}")
        return jsonify({'last_24h': [], 'last_bullish': None, 'last_bearish': None, 'total_signals': 0, 'error': str(e)}), 200
