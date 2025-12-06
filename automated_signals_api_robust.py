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
        Get complete dashboard data from automated_signals table.
        
        STRICT PATCH:
        - Returns ALL active trades (no limit) so they never disappear
        - Returns capped completed trades (last 500) for pagination
        - Only uses automated_signals table
        - NO legacy tables: live_signals, signal_lab_trades, enhanced_signals_v2
        """
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from decimal import Decimal
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'no_database_url',
                    'active_trades': [],
                    'completed_trades': [],
                    'stats': _get_empty_stats_ultra()
                }), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Check table existence
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'automated_signals'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.warning("automated_signals table does not exist")
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'table_not_found',
                    'active_trades': [],
                    'completed_trades': [],
                    'stats': _get_empty_stats_ultra()
                }), 200
            
            cursor.close()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Helper to convert row to JSON-serializable dict
            def row_to_dict(row):
                result = {}
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        result[key] = float(value)
                    elif hasattr(value, 'isoformat'):
                        result[key] = value.isoformat()
                    else:
                        result[key] = value
                return result
            
            # ============================================
            # STEP 1: Load ALL ACTIVE trades (NO LIMIT)
            # ACTIVE = trades without any EXIT event
            # FIX: Properly aggregate ENTRY data with latest MFE
            # ============================================
            cursor.execute("""
                WITH entry_data AS (
                    SELECT 
                        trade_id,
                        direction,
                        entry_price,
                        stop_loss,
                        session,
                        bias,
                        timestamp as entry_timestamp
                    FROM automated_signals
                    WHERE event_type = 'ENTRY'
                ),
                latest_mfe AS (
                    SELECT DISTINCT ON (trade_id)
                        trade_id,
                        mfe,
                        be_mfe,
                        no_be_mfe,
                        current_price,
                        timestamp as last_update
                    FROM automated_signals
                    WHERE event_type IN ('ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED')
                    ORDER BY trade_id, timestamp DESC
                ),
                active_trade_ids AS (
                    SELECT DISTINCT trade_id
                    FROM automated_signals
                    WHERE event_type = 'ENTRY'
                    AND trade_id NOT IN (
                        SELECT DISTINCT trade_id 
                        FROM automated_signals 
                        WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
                    )
                )
                SELECT 
                    e.trade_id,
                    'ACTIVE' as trade_status,
                    e.direction,
                    e.entry_price,
                    e.stop_loss,
                    e.session,
                    e.bias,
                    e.entry_timestamp as timestamp,
                    COALESCE(m.mfe, 0) as mfe,
                    COALESCE(m.be_mfe, 0) as be_mfe,
                    COALESCE(m.no_be_mfe, 0) as no_be_mfe,
                    m.current_price,
                    NULL as final_mfe
                FROM active_trade_ids a
                JOIN entry_data e ON a.trade_id = e.trade_id
                LEFT JOIN latest_mfe m ON a.trade_id = m.trade_id
                ORDER BY e.entry_timestamp DESC
            """)
            active_rows = cursor.fetchall()
            active_trades = [row_to_dict(row) for row in active_rows]
            
            # ============================================
            # STEP 2: Load COMPLETED trades with LIMIT 500
            # COMPLETED = trades with EXIT event
            # FIX: Join ENTRY data with EXIT data for complete info
            # ============================================
            cursor.execute("""
                WITH entry_data AS (
                    SELECT 
                        trade_id,
                        direction,
                        entry_price,
                        stop_loss,
                        session,
                        bias,
                        timestamp as entry_timestamp
                    FROM automated_signals
                    WHERE event_type = 'ENTRY'
                ),
                exit_data AS (
                    SELECT 
                        trade_id,
                        event_type as exit_type,
                        final_mfe,
                        mfe as exit_mfe,
                        be_mfe as exit_be_mfe,
                        no_be_mfe as exit_no_be_mfe,
                        timestamp as exit_timestamp
                    FROM automated_signals
                    WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
                )
                SELECT 
                    x.trade_id,
                    x.exit_type as event_type,
                    'COMPLETED' as trade_status,
                    COALESCE(e.direction, 'UNKNOWN') as direction,
                    e.entry_price,
                    e.stop_loss,
                    e.session,
                    e.bias,
                    x.exit_timestamp as timestamp,
                    COALESCE(x.exit_mfe, 0) as mfe,
                    COALESCE(x.exit_be_mfe, 0) as be_mfe,
                    COALESCE(x.exit_no_be_mfe, 0) as no_be_mfe,
                    x.final_mfe
                FROM exit_data x
                LEFT JOIN entry_data e ON x.trade_id = e.trade_id
                ORDER BY x.exit_timestamp DESC
                LIMIT 500
            """)
            completed_rows = cursor.fetchall()
            completed_trades = [row_to_dict(row) for row in completed_rows]
            
            # ============================================
            # STEP 3: Calculate stats
            # ============================================
            
            # Today's count (Eastern Time)
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND timestamp AT TIME ZONE 'America/New_York' >= CURRENT_DATE AT TIME ZONE 'America/New_York'
            """)
            today_count = cursor.fetchone()['count'] or 0
            
            # Active count (unique trades without EXIT)
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND trade_id NOT IN (
                    SELECT DISTINCT trade_id 
                    FROM automated_signals 
                    WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
                )
            """)
            active_count = cursor.fetchone()['count'] or 0
            
            # Completed count (total, not just returned)
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
            """)
            completed_count = cursor.fetchone()['count'] or 0
            
            # Last webhook timestamp
            cursor.execute("""
                SELECT MAX(timestamp) as last_ts FROM automated_signals
            """)
            last_ts_row = cursor.fetchone()
            last_webhook_timestamp = last_ts_row['last_ts'].isoformat() if last_ts_row and last_ts_row['last_ts'] else None
            
            # Webhook healthy check (within 5 minutes = 300 seconds)
            webhook_healthy = False
            if last_ts_row and last_ts_row['last_ts']:
                last_ts = last_ts_row['last_ts']
                if last_ts.tzinfo is None:
                    last_ts = pytz.UTC.localize(last_ts)
                now_utc = datetime.now(pytz.UTC)
                delta_sec = (now_utc - last_ts).total_seconds()
                webhook_healthy = delta_sec < 300
            
            # Average MFE from completed trades
            cursor.execute("""
                SELECT AVG(COALESCE(final_mfe, mfe)) as avg_mfe
                FROM automated_signals
                WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
            """)
            avg_mfe_row = cursor.fetchone()
            avg_mfe = float(avg_mfe_row['avg_mfe']) if avg_mfe_row and avg_mfe_row['avg_mfe'] else 0.0
            
            # Win rate (final_mfe > 0 is a win)
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE COALESCE(final_mfe, mfe, 0) > 0) as wins,
                    COUNT(*) as total
                FROM automated_signals
                WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
            """)
            win_row = cursor.fetchone()
            wins = win_row['wins'] or 0
            total_exits = win_row['total'] or 0
            win_rate = (wins / total_exits * 100) if total_exits > 0 else 0.0
            
            stats = {
                'today_count': today_count,
                'active_count': active_count,
                'completed_count': completed_count,
                'last_webhook_timestamp': last_webhook_timestamp,
                'webhook_healthy': webhook_healthy,
                'avg_mfe': round(avg_mfe, 2),
                'win_rate': round(win_rate, 1)
            }
            
            cursor.close()
            conn.close()
            
            # Build response matching Ultra JS expectations
            response = jsonify({
                'success': True,
                'active_trades': active_trades,
                'completed_trades': completed_trades,
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            
            # Cache-busting headers
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
                'active_trades': [],
                'completed_trades': [],
                'stats': _get_empty_stats_ultra()
            }), 200
    
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
                    stop_loss, session, bias, risk_distance,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp
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
            
            # Convert to events list - keep datetime objects for build_trade_state
            events = []
            for row in rows:
                event = dict(row)
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
            
            # Helper to safely convert to float
            def safe_float(val):
                if val is None:
                    return None
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return None
            
            # Build detailed response - aligned with build_trade_state output
            detail = {
                'trade_id': trade_state['trade_id'],
                'direction': trade_state['direction'],
                'session': trade_state['session'],
                'status': trade_state['status'],
                'entry_price': safe_float(trade_state.get('entry_price')),
                'stop_loss': safe_float(trade_state.get('stop_loss')),
                'current_mfe': safe_float(trade_state.get('no_be_mfe_R') or trade_state.get('be_mfe_R')),
                'final_mfe': safe_float(trade_state.get('final_mfe_R')),
                'exit_price': safe_float(trade_state.get('exit_price')),
                'exit_reason': trade_state.get('completed_reason'),
                'be_triggered': trade_state.get('status') == 'BE_PROTECTED',
                'targets': trade_state.get('targets'),
                'setup': {
                    'family': trade_state.get('setup_family'),
                    'variant': trade_state.get('setup_variant'),
                    'id': trade_state.get('setup_id'),
                    'signal_strength': trade_state.get('setup_strength')
                },
                'market_state_entry': {
                    'trend_regime': trade_state.get('market_trend_regime'),
                    'volatility_regime': trade_state.get('market_vol_regime')
                },
                'events': []
            }
            
            # Add events timeline
            for event in events:
                # Safely convert timestamp
                ts = event.get('timestamp')
                ts_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts) if ts else None
                
                event_data = {
                    'event_type': event.get('event_type'),
                    'timestamp': ts_str,
                    'be_mfe_R': safe_float(event.get('be_mfe')),
                    'no_be_mfe_R': safe_float(event.get('no_be_mfe')),
                    'mfe_R': safe_float(event.get('mfe')),
                    'mae_R': None,
                    'current_price': safe_float(event.get('current_price')),
                    'exit_price': safe_float(event.get('exit_price'))
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


    @app.route('/api/automated-signals/daily-calendar')
    def get_daily_calendar():
        """Get daily trade data for calendar view with completed and active counts"""
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({'success': False, 'error': 'no_database_url'}), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get completed trades per day (last 90 days)
            cursor.execute("""
                SELECT 
                    DATE(timestamp AT TIME ZONE 'America/New_York') as date,
                    COUNT(DISTINCT trade_id) as completed_count,
                    AVG(COALESCE(final_mfe, no_be_mfe, mfe, 0)) as avg_mfe
                FROM automated_signals
                WHERE timestamp >= CURRENT_DATE - INTERVAL '90 days'
                AND event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
                GROUP BY DATE(timestamp AT TIME ZONE 'America/New_York')
            """)
            completed_by_date = {row['date'].strftime('%Y-%m-%d'): row for row in cursor.fetchall()}
            
            # Get active trades per day (entry date, no exit yet)
            cursor.execute("""
                SELECT 
                    DATE(e.timestamp AT TIME ZONE 'America/New_York') as date,
                    COUNT(DISTINCT e.trade_id) as active_count
                FROM automated_signals e
                WHERE e.event_type = 'ENTRY'
                AND e.timestamp >= CURRENT_DATE - INTERVAL '90 days'
                AND e.trade_id NOT IN (
                    SELECT DISTINCT trade_id 
                    FROM automated_signals 
                    WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN', 'EXIT_SL', 'EXIT_BE')
                )
                GROUP BY DATE(e.timestamp AT TIME ZONE 'America/New_York')
            """)
            active_by_date = {row['date'].strftime('%Y-%m-%d'): row['active_count'] for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            
            # Merge data
            all_dates = set(completed_by_date.keys()) | set(active_by_date.keys())
            daily_data = {}
            
            for date_str in all_dates:
                completed_info = completed_by_date.get(date_str, {})
                daily_data[date_str] = {
                    'completed_count': completed_info.get('completed_count', 0) if completed_info else 0,
                    'active_count': active_by_date.get(date_str, 0),
                    'avg_mfe': float(completed_info.get('avg_mfe', 0)) if completed_info and completed_info.get('avg_mfe') else 0,
                    'trade_count': (completed_info.get('completed_count', 0) if completed_info else 0) + active_by_date.get(date_str, 0)
                }
            
            return jsonify({
                'success': True,
                'daily_data': daily_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching daily calendar: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
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

    @app.route('/api/automated-signals/integrity')
    def get_integrity_report():
        """
        Returns full integrity results for all trades using the new
        check_trade_integrity() and build_integrity_report_for_trade() engine.
        """
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from automated_signals_state import build_trade_state, build_integrity_report_for_trade
            import os
            
            database_url = os.environ.get('DATABASE_URL')
            logger.warning(f"[INTEGRITY_DB_URL] Using DATABASE_URL = {database_url}")
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Fetch all events for all trades
            cursor.execute("""
                SELECT
                    id, trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp
                FROM automated_signals
                ORDER BY trade_id, timestamp ASC;
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Group by trade_id
            grouped = {}
            for r in rows:
                tid = r["trade_id"]
                grouped.setdefault(tid, []).append(r)
            
            issues = []
            for trade_id, evs in grouped.items():
                state = build_trade_state(evs)
                if not state:
                    continue
                
                rep = build_integrity_report_for_trade(evs, state)
                issues.append({
                    "trade_id": trade_id,
                    "healthy": rep["healthy"],
                    "failures": rep["all_failures"],
                    "categories": rep["categories"]
                })
            
            return jsonify({"issues": issues}), 200
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

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


def _get_empty_stats_ultra():
    """Return empty stats structure for Ultra dashboard"""
    return {
        'today_count': 0,
        'active_count': 0,
        'completed_count': 0,
        'last_webhook_timestamp': None,
        'webhook_healthy': False,
        'avg_mfe': 0.0,
        'win_rate': 0.0
    }
