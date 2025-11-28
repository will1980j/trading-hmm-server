"""
Robust Automated Signals API
Production-grade implementation with comprehensive error handling
"""

from flask import jsonify
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

def register_automated_signals_api_robust(app, db):
    """Register robust API endpoints with comprehensive error handling"""
    
    @app.route('/api/automated-signals/dashboard-data')
    def get_dashboard_data_robust():
        """
        Get complete dashboard data with robust error handling
        Handles multiple data scenarios and provides meaningful fallbacks
        """
        try:
            # Use fresh connection instead of db.conn
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'no_database_url',
                    'active_trades': [],
                    'completed_trades': []
                }), 500
            
            conn = psycopg2.connect(database_url)
            # Use regular cursor for simple queries, RealDictCursor for data queries
            cursor = conn.cursor()
            
            # Strategy 1: Check table existence
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'automated_signals'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.warning("automated_signals table does not exist")
                return jsonify({
                    'success': False,
                    'error': 'table_not_found',
                    'message': 'Automated signals table not initialized',
                    'active_trades': [],
                    'completed_trades': [],
                    'stats': _get_empty_stats(),
                    'hourly_distribution': {},
                    'session_breakdown': {}
                }), 200
            
            # Strategy 2: Check for any data
            cursor.execute("SELECT COUNT(*) FROM automated_signals;")
            total_records = cursor.fetchone()[0]
            
            if total_records == 0:
                logger.info("automated_signals table is empty")
                return jsonify({
                    'success': True,
                    'message': 'No signals received yet',
                    'active_trades': [],
                    'completed_trades': [],
                    'stats': _get_empty_stats(),
                    'hourly_distribution': {},
                    'session_breakdown': {},
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }), 200
            
            # Strategy 3: Get column information
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'automated_signals'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            has_signal_time = 'signal_date' in columns and 'signal_time' in columns
            
            logger.info(f"Table has {total_records} records, columns: {columns}")
            
            # Close regular cursor and open RealDictCursor for data queries
            cursor.close()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Strategy 4: Get active trades with comprehensive error handling
            active_trades = _get_active_trades_robust(cursor, has_signal_time)
            
            # Strategy 5: Get completed trades
            completed_trades = _get_completed_trades_robust(cursor, has_signal_time)
            
            # Strategy 6: Calculate statistics
            stats = _calculate_stats_robust(cursor, active_trades, completed_trades)
            
            # Strategy 7: Get distributions
            hourly_dist = _get_hourly_distribution_robust(cursor)
            session_breakdown = _get_session_breakdown_robust(cursor)
            
            cursor.close()
            conn.close()
            
            # Create response with cache-busting headers
            response = jsonify({
                'success': True,
                'active_trades': active_trades,
                'completed_trades': completed_trades,
                'stats': stats,
                'hourly_distribution': hourly_dist,
                'session_breakdown': session_breakdown,
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'debug_info': {
                    'total_records': total_records,
                    'has_signal_time_columns': has_signal_time,
                    'active_count': len(active_trades),
                    'completed_count': len(completed_trades)
                }
            })
            
            # CRITICAL: Add cache-busting headers to prevent stale data
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response, 200
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Dashboard data error: {error_msg}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'query_failed',
                'message': error_msg,
                'error_type': type(e).__name__,
                'error_details': str(e),
                'active_trades': [],
                'completed_trades': [],
                'stats': _get_empty_stats(),
                'hourly_distribution': {},
                'session_breakdown': {}
            }), 200  # Return 200 to prevent frontend errors
    
    @app.route('/api/automated-signals/stats')
    def get_stats_robust():
        """
        Get dashboard statistics with robust error handling
        Returns basic stats for health checks and quick overview
        """
        try:
            cursor = db.conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'automated_signals'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return jsonify({
                    'success': True,
                    'stats': _get_empty_stats(),
                    'message': 'Table not initialized'
                }), 200
            
            # STEP 1: Query most recent webhook timestamp
            cursor.execute("""
                SELECT MAX(timestamp) FROM automated_signals;
            """)
            last_ts = cursor.fetchone()[0]
            
            # STEP 2: Compute webhook_healthy status
            if last_ts is not None:
                now_utc = datetime.now(pytz.UTC)
                # Ensure last_ts is timezone-aware
                if last_ts.tzinfo is None:
                    last_ts = pytz.UTC.localize(last_ts)
                delta_sec = (now_utc - last_ts).total_seconds()
                webhook_healthy = delta_sec < 90
            else:
                webhook_healthy = False
                delta_sec = None
            
            # Get basic counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT trade_id) as unique_trades,
                    COUNT(CASE WHEN event_type = 'ENTRY' THEN 1 END) as entries,
                    COUNT(CASE WHEN event_type LIKE 'EXIT_%' THEN 1 END) as exits
                FROM automated_signals;
            """)
            row = cursor.fetchone()
            
            stats = {
                'total_signals': row[0] if row else 0,
                'unique_trades': row[1] if row else 0,
                'entries': row[2] if row else 0,
                'exits': row[3] if row else 0,
                'active_count': (row[2] - row[3]) if row else 0,
                'completed_count': row[3] if row else 0,
                'webhook_healthy': webhook_healthy,
                'last_webhook_timestamp': last_ts.isoformat() if last_ts else None,
                'seconds_since_last_webhook': round(delta_sec, 1) if delta_sec is not None else None
            }
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Stats error: {e}", exc_info=True)
            return jsonify({
                'success': True,
                'stats': _get_empty_stats(),
                'error': str(e)
            }), 200


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


def _get_active_trades_robust(cursor, has_signal_time):
    """Get active trades with telemetry support"""
    try:
        # Import state builder
        from automated_signals_state import build_trade_state
        
        # Get all trade_ids for active trades
        cursor.execute("""
            SELECT trade_id
            FROM (
                SELECT trade_id, MAX(timestamp) AS last_event
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND trade_id NOT IN (
                    SELECT trade_id FROM automated_signals 
                    WHERE event_type LIKE 'EXIT_%'
                )
                GROUP BY trade_id
            ) AS sub
            ORDER BY sub.last_event DESC
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


def _get_completed_trades_robust(cursor, has_signal_time):
    """Get completed trades with telemetry support"""
    try:
        # Import state builder
        from automated_signals_state import build_trade_state
        
        # Get all trade_ids for completed trades
        cursor.execute("""
            SELECT trade_id
            FROM (
                SELECT trade_id, MAX(timestamp) AS last_event
                FROM automated_signals
                WHERE event_type LIKE 'EXIT_%'
                GROUP BY trade_id
            ) AS sub
            ORDER BY sub.last_event DESC
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


def _calculate_stats_robust(cursor, active_trades, completed_trades):
    """Calculate statistics with robust error handling"""
    try:
        total_signals = len(active_trades) + len(completed_trades)
        active_count = len(active_trades)
        completed_count = len(completed_trades)
        
        # Calculate MFE statistics
        all_mfes = []
        for trade in active_trades:
            if trade.get('current_mfe'):
                all_mfes.append(trade['current_mfe'])
        for trade in completed_trades:
            if trade.get('final_mfe'):
                all_mfes.append(trade['final_mfe'])
        
        avg_mfe = sum(all_mfes) / len(all_mfes) if all_mfes else 0.0
        
        # Calculate win rate (trades that hit targets)
        wins = sum(1 for t in completed_trades if t.get('exit_type') == 'EXIT_TARGET')
        win_rate = (wins / completed_count * 100) if completed_count > 0 else 0.0
        
        return {
            'total_signals': total_signals,
            'active_count': active_count,
            'completed_count': completed_count,
            'pending_count': 0,  # For future use
            'avg_mfe': round(avg_mfe, 2),
            'win_count': wins,
            'win_rate': round(win_rate, 1),
            'success_rate': round(win_rate, 1)
        }
        
    except Exception as e:
        logger.error(f"Error calculating stats: {e}", exc_info=True)
        return _get_empty_stats()

def _get_hourly_distribution_robust(cursor):
    """Get hourly distribution with error handling"""
    try:
        cursor.execute("""
            SELECT 
                EXTRACT(HOUR FROM timestamp AT TIME ZONE 'America/New_York') as hour,
                COUNT(*) as count
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND timestamp > NOW() - INTERVAL '30 days'
            GROUP BY hour
            ORDER BY hour;
        """)
        
        distribution = {}
        for row in cursor.fetchall():
            hour = int(row[0])
            count = row[1]
            distribution[str(hour)] = count
        
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting hourly distribution: {e}", exc_info=True)
        return {}

def _get_session_breakdown_robust(cursor):
    """Get session breakdown with error handling"""
    try:
        cursor.execute("""
            SELECT 
                session,
                COUNT(*) as count,
                AVG(CAST(mfe AS FLOAT)) as avg_mfe
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND timestamp > NOW() - INTERVAL '30 days'
            GROUP BY session
            ORDER BY count DESC;
        """)
        
        breakdown = {}
        for row in cursor.fetchall():
            session = row[0] or 'Unknown'
            breakdown[session] = {
                'count': row[1],
                'avg_mfe': round(float(row[2]) if row[2] else 0.0, 2)
            }
        
        return breakdown
        
    except Exception as e:
        logger.error(f"Error getting session breakdown: {e}", exc_info=True)
        return {}

def _format_duration(duration):
    """Format timedelta as human-readable string"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def _get_empty_stats():
    """Return empty stats structure"""
    return {
        'total_signals': 0,
        'active_count': 0,
        'completed_count': 0,
        'pending_count': 0,
        'avg_mfe': 0.0,
        'win_count': 0,
        'win_rate': 0.0,
        'success_rate': 0.0
    }
