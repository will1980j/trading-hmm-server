"""
Add trade detail endpoint to web_server.py
This endpoint returns all events for a specific trade_id
"""

endpoint_code = '''
@app.route('/api/automated-signals/trade-detail/<trade_id>', methods=['GET'])
def get_trade_detail(trade_id):
    """Get complete event history for a specific trade"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({"success": False, "error": "DATABASE_URL not configured"}), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get all events for this trade_id
        cursor.execute("""
            SELECT 
                id, trade_id, event_type, direction, entry_price, stop_loss,
                risk_distance, be_mfe, no_be_mfe, session, bias,
                signal_date, signal_time, timestamp
            FROM automated_signals
            WHERE trade_id = %s
            ORDER BY timestamp ASC
        """, (trade_id,))
        
        events = []
        trade_info = None
        
        for row in cursor.fetchall():
            event = {
                "id": row[0],
                "trade_id": row[1],
                "event_type": row[2],
                "direction": row[3],
                "entry_price": float(row[4]) if row[4] else None,
                "stop_loss": float(row[5]) if row[5] else None,
                "risk_distance": float(row[6]) if row[6] else None,
                "be_mfe": float(row[7]) if row[7] is not None else None,
                "no_be_mfe": float(row[8]) if row[8] is not None else None,
                "session": row[9],
                "bias": row[10],
                "signal_date": row[11].isoformat() if row[11] else None,
                "signal_time": row[12].isoformat() if row[12] else None,
                "timestamp": row[13].isoformat() if row[13] else None
            }
            events.append(event)
            
            # Use first event for trade info
            if not trade_info:
                trade_info = event.copy()
        
        cursor.close()
        conn.close()
        
        if not events:
            return jsonify({
                "success": False,
                "error": f"No events found for trade_id: {trade_id}"
            }), 404
        
        # Get latest MFE values from last event
        latest_event = events[-1]
        trade_info['be_mfe'] = latest_event['be_mfe']
        trade_info['no_be_mfe'] = latest_event['no_be_mfe']
        trade_info['events'] = events
        
        return jsonify({
            "success": True,
            "trade": trade_info
        }), 200
        
    except Exception as e:
        logger.error(f"Trade detail error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
'''

print("Add this endpoint to web_server.py after the dashboard-data endpoint:")
print(endpoint_code)
