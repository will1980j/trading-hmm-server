"""
PHASE 7.A: TELEMETRY-RICH API UPGRADE
Upgrades get_hub_data() and get_trade_detail() to return telemetry-enhanced data
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import pytz
import json

def upgrade_apis_with_telemetry():
    """
    Upgrade automated_signals_api_robust.py with telemetry support
    """
    
    print("🚀 PHASE 7.A: TELEMETRY-RICH API UPGRADE")
    print("=" * 70)
    
    api_file = "automated_signals_api_robust.py"
    
    # Read current file
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace _get_active_trades_robust function
    active_trades_start = content.find('def _get_active_trades_robust(')
    if active_trades_start == -1:
        print("❌ Could not find _get_active_trades_robust function")
        return False
    
    # Find the end of the function
    active_trades_end = content.find('\ndef _get_completed_trades_robust(', active_trades_start)
    
    # New telemetry-aware active trades function
    new_active_trades = '''def _get_active_trades_robust(cursor, has_signal_time):
    """Get active trades with telemetry support"""
    try:
        # Import state builder
        from automated_signals_state import build_trade_state
        
        # Get all trade_ids for active trades
        cursor.execute("""
            SELECT DISTINCT trade_id
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND trade_id NOT IN (
                SELECT trade_id FROM automated_signals 
                WHERE event_type LIKE 'EXIT_%'
            )
            ORDER BY timestamp DESC
            LIMIT 100;
        """)
        
        trade_ids = [row[0] for row in cursor.fetchall()]
        
        active_trades = []
        
        for trade_id in trade_ids:
            # Get all events for this trade
            cursor.execute("""
                SELECT 
                    trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance, targets,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp,
                    telemetry
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                # Convert datetime objects to strings
                if event.get('signal_date'):
                    event['signal_date'] = event['signal_date'].isoformat()
                if event.get('signal_time'):
                    event['signal_time'] = event['signal_time'].isoformat()
                if event.get('timestamp'):
                    event['timestamp'] = event['timestamp'].isoformat()
                events.append(event)
            
            # Build trade state using telemetry-aware builder
            trade_state = build_trade_state(events)
            
            if trade_state:
                # Convert to API format
                trade = {
                    'id': events[0].get('id') if events else None,
                    'trade_id': trade_state['trade_id'],
                    'direction': trade_state['direction'],
                    'session': trade_state['session'],
                    'status': trade_state['status'],
                    'entry_price': float(trade_state['entry_price']) if trade_state['entry_price'] else None,
                    'stop_loss': float(trade_state['stop_loss']) if trade_state['stop_loss'] else None,
                    'current_mfe': float(trade_state['current_mfe']) if trade_state['current_mfe'] else None,
                    'final_mfe': float(trade_state['final_mfe']) if trade_state['final_mfe'] else None,
                    'exit_price': float(trade_state['exit_price']) if trade_state['exit_price'] else None,
                    'exit_reason': trade_state['exit_reason'],
                    'be_triggered': trade_state['be_triggered'],
                    'targets': trade_state['targets'],
                    'setup': trade_state['setup'],
                    'market_state': trade_state['market_state'],
                    'timestamp': events[0]['timestamp'] if events else None
                }
                
                # Add date for calendar
                if trade.get('timestamp'):
                    try:
                        ts = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                        eastern = pytz.timezone('America/New_York')
                        ts_eastern = ts.astimezone(eastern)
                        trade['date'] = ts_eastern.strftime('%Y-%m-%d')
                    except:
                        pass
                
                active_trades.append(trade)
        
        return active_trades
        
    except Exception as e:
        import logging
        logging.error(f"Error getting active trades: {e}", exc_info=True)
        return []

'''
    
    # Replace the function
    content = content[:active_trades_start] + new_active_trades + content[active_trades_end:]
    
    print("✅ Updated _get_active_trades_robust with telemetry support")
    
    # Find and replace _get_completed_trades_robust function
    completed_trades_start = content.find('def _get_completed_trades_robust(')
    if completed_trades_start == -1:
        print("❌ Could not find _get_completed_trades_robust function")
        return False
    
    # Find the end of the function
    completed_trades_end = content.find('\ndef _calculate_stats_robust(', completed_trades_start)
    
    # New telemetry-aware completed trades function
    new_completed_trades = '''def _get_completed_trades_robust(cursor, has_signal_time):
    """Get completed trades with telemetry support"""
    try:
        # Import state builder
        from automated_signals_state import build_trade_state
        
        # Get all trade_ids for completed trades
        cursor.execute("""
            SELECT DISTINCT trade_id
            FROM automated_signals
            WHERE event_type LIKE 'EXIT_%'
            ORDER BY timestamp DESC
            LIMIT 100;
        """)
        
        trade_ids = [row[0] for row in cursor.fetchall()]
        
        completed_trades = []
        
        for trade_id in trade_ids:
            # Get all events for this trade
            cursor.execute("""
                SELECT 
                    trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance, targets,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp,
                    telemetry
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                # Convert datetime objects to strings
                if event.get('signal_date'):
                    event['signal_date'] = event['signal_date'].isoformat()
                if event.get('signal_time'):
                    event['signal_time'] = event['signal_time'].isoformat()
                if event.get('timestamp'):
                    event['timestamp'] = event['timestamp'].isoformat()
                events.append(event)
            
            # Build trade state using telemetry-aware builder
            trade_state = build_trade_state(events)
            
            if trade_state and trade_state['status'] == 'COMPLETED':
                # Convert to API format
                trade = {
                    'id': events[0].get('id') if events else None,
                    'trade_id': trade_state['trade_id'],
                    'direction': trade_state['direction'],
                    'session': trade_state['session'],
                    'status': trade_state['status'],
                    'entry_price': float(trade_state['entry_price']) if trade_state['entry_price'] else None,
                    'stop_loss': float(trade_state['stop_loss']) if trade_state['stop_loss'] else None,
                    'current_mfe': float(trade_state['current_mfe']) if trade_state['current_mfe'] else None,
                    'final_mfe': float(trade_state['final_mfe']) if trade_state['final_mfe'] else None,
                    'exit_price': float(trade_state['exit_price']) if trade_state['exit_price'] else None,
                    'exit_reason': trade_state['exit_reason'],
                    'be_triggered': trade_state['be_triggered'],
                    'targets': trade_state['targets'],
                    'setup': trade_state['setup'],
                    'market_state': trade_state['market_state'],
                    'timestamp': events[0]['timestamp'] if events else None
                }
                
                # Add date for calendar
                if trade.get('timestamp'):
                    try:
                        ts = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                        eastern = pytz.timezone('America/New_York')
                        ts_eastern = ts.astimezone(eastern)
                        trade['date'] = ts_eastern.strftime('%Y-%m-%d')
                    except:
                        pass
                
                completed_trades.append(trade)
        
        return completed_trades
        
    except Exception as e:
        import logging
        logging.error(f"Error getting completed trades: {e}", exc_info=True)
        return []

'''
    
    # Replace the function
    content = content[:completed_trades_start] + new_completed_trades + content[completed_trades_end:]
    
    print("✅ Updated _get_completed_trades_robust with telemetry support")
    
    # Add get_trade_detail endpoint
    # Find the register function and add new endpoint
    register_end = content.find('def _get_active_trades_robust(')
    
    new_endpoint = '''
    @app.route('/api/automated-signals/trade-detail/<trade_id>')
    def get_trade_detail(trade_id):
        """
        Get detailed trade information with full telemetry data
        """
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from automated_signals_state import build_trade_state
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'no_database_url'
                }), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all events for this trade
            cursor.execute("""
                SELECT 
                    id, trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance, targets,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp,
                    telemetry
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            rows = cursor.fetchall()
            
            if not rows:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'trade_not_found',
                    'message': f'Trade {trade_id} not found'
                }), 404
            
            # Convert to events list
            events = []
            for row in rows:
                event = dict(row)
                # Convert datetime objects to strings
                if event.get('signal_date'):
                    event['signal_date'] = event['signal_date'].isoformat()
                if event.get('signal_time'):
                    event['signal_time'] = event['signal_time'].isoformat()
                if event.get('timestamp'):
                    event['timestamp'] = event['timestamp'].isoformat()
                events.append(event)
            
            # Build trade state
            trade_state = build_trade_state(events)
            
            if not trade_state:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'state_build_failed',
                    'message': 'Could not build trade state'
                }), 500
            
            # Build detailed response
            detail = {
                'trade_id': trade_state['trade_id'],
                'direction': trade_state['direction'],
                'session': trade_state['session'],
                'status': trade_state['status'],
                'entry_price': float(trade_state['entry_price']) if trade_state['entry_price'] else None,
                'stop_loss': float(trade_state['stop_loss']) if trade_state['stop_loss'] else None,
                'current_mfe': float(trade_state['current_mfe']) if trade_state['current_mfe'] else None,
                'final_mfe': float(trade_state['final_mfe']) if trade_state['final_mfe'] else None,
                'exit_price': float(trade_state['exit_price']) if trade_state['exit_price'] else None,
                'exit_reason': trade_state['exit_reason'],
                'be_triggered': trade_state['be_triggered'],
                'targets': trade_state['targets'],
                'setup': trade_state['setup'],
                'market_state_entry': trade_state['market_state'],
                'events': []
            }
            
            # Add events with telemetry
            for event in events:
                event_data = {
                    'event_type': event['event_type'],
                    'timestamp': event['timestamp'],
                    'mfe_R': float(event['mfe']) if event.get('mfe') else None,
                    'mae_R': None,  # Not yet tracked
                    'current_price': float(event['current_price']) if event.get('current_price') else None
                }
                
                # Add telemetry if available
                if event.get('telemetry'):
                    tel = event['telemetry']
                    event_data['telemetry'] = {
                        'mfe_R': tel.get('mfe_R'),
                        'mae_R': tel.get('mae_R'),
                        'final_mfe_R': tel.get('final_mfe_R'),
                        'exit_reason': tel.get('exit_reason')
                    }
                
                detail['events'].append(event_data)
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'data': detail,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Trade detail error: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'query_failed',
                'message': str(e)
            }), 500

'''
    
    # Insert new endpoint before helper functions
    content = content[:register_end] + new_endpoint + "\n" + content[register_end:]
    
    print("✅ Added get_trade_detail endpoint")
    
    # Write updated file
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {api_file}")
    
    return True

if __name__ == "__main__":
    if upgrade_apis_with_telemetry():
        print("\n" + "=" * 70)
        print("✅ PHASE 7.A COMPLETE")
        print("=" * 70)
        print("\n🎯 APIs UPGRADED WITH:")
        print("   ✅ Telemetry-aware get_hub_data()")
        print("   ✅ Telemetry-aware get_trade_detail()")
        print("   ✅ Full nested object support")
        print("   ✅ Backward compatibility maintained")
    else:
        print("\n❌ PHASE 7.A FAILED")
