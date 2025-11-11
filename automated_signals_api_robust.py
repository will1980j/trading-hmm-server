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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
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
            
            return jsonify({
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
            }), 200
            
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
                'completed_count': row[3] if row else 0
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

def _get_active_trades_robust(cursor, has_signal_time):
    """Get active trades with multiple fallback strategies"""
    try:
        time_columns = "e.signal_date, e.signal_time," if has_signal_time else ""
        
        query = f"""
            SELECT 
                e.id,
                e.trade_id,
                e.direction as bias,
                CAST(e.entry_price AS FLOAT) as entry_price,
                CAST(e.stop_loss AS FLOAT) as stop_loss_price,
                CAST(COALESCE(m.mfe, e.mfe, 0) AS FLOAT) as current_mfe,
                e.session,
                {time_columns}
                e.timestamp as created_at,
                'ACTIVE' as trade_status
            FROM automated_signals e
            LEFT JOIN LATERAL (
                SELECT mfe, current_price
                FROM automated_signals
                WHERE trade_id = e.trade_id
                AND event_type = 'MFE_UPDATE'
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON true
            WHERE e.event_type = 'ENTRY'
            AND e.trade_id NOT IN (
                SELECT trade_id FROM automated_signals 
                WHERE event_type LIKE 'EXIT_%'
            )
            ORDER BY e.timestamp DESC
            LIMIT 100;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        active_trades = []
        now = datetime.now(pytz.timezone('US/Eastern'))
        
        for row in rows:
            trade = dict(row)
            
            # Ensure numeric fields
            for field in ['entry_price', 'stop_loss_price', 'current_mfe']:
                if trade.get(field):
                    trade[field] = float(trade[field])
            
            # Calculate duration and add date field for calendar
            if trade.get('created_at'):
                created = trade['created_at']
                if created.tzinfo is None:
                    created = pytz.timezone('US/Eastern').localize(created)
                duration = now - created
                trade['duration_seconds'] = int(duration.total_seconds())
                trade['duration_display'] = _format_duration(duration)
                # Add date field in YYYY-MM-DD format for calendar
                trade['date'] = created.strftime('%Y-%m-%d')
            
            active_trades.append(trade)
        
        logger.info(f"Found {len(active_trades)} active trades")
        return active_trades
        
    except Exception as e:
        logger.error(f"Error getting active trades: {e}", exc_info=True)
        return []

def _get_completed_trades_robust(cursor, has_signal_time):
    """Get completed trades with multiple fallback strategies"""
    try:
        time_columns = "e.signal_date, e.signal_time," if has_signal_time else ""
        
        query = f"""
            SELECT 
                e.id,
                e.trade_id,
                e.direction as bias,
                CAST(e.entry_price AS FLOAT) as entry_price,
                CAST(e.stop_loss AS FLOAT) as stop_loss_price,
                CAST(COALESCE(ex.final_mfe, e.mfe, 0) AS FLOAT) as final_mfe,
                ex.exit_type,
                ex.exit_price,
                e.session,
                {time_columns}
                e.timestamp as created_at,
                ex.timestamp as exit_time,
                'COMPLETED' as trade_status
            FROM automated_signals e
            INNER JOIN LATERAL (
                SELECT 
                    event_type as exit_type,
                    CAST(exit_price AS FLOAT) as exit_price,
                    CAST(mfe AS FLOAT) as final_mfe,
                    timestamp
                FROM automated_signals
                WHERE trade_id = e.trade_id
                AND event_type LIKE 'EXIT_%'
                ORDER BY timestamp DESC
                LIMIT 1
            ) ex ON true
            WHERE e.event_type = 'ENTRY'
            ORDER BY ex.timestamp DESC
            LIMIT 100;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        completed_trades = []
        
        for row in rows:
            trade = dict(row)
            
            # Ensure numeric fields
            for field in ['entry_price', 'stop_loss_price', 'final_mfe', 'exit_price']:
                if trade.get(field):
                    trade[field] = float(trade[field])
            
            # Calculate trade duration and add date field for calendar
            if trade.get('created_at'):
                created = trade['created_at']
                if created.tzinfo is None:
                    created = pytz.timezone('US/Eastern').localize(created)
                # Add date field in YYYY-MM-DD format for calendar
                trade['date'] = created.strftime('%Y-%m-%d')
                
                if trade.get('exit_time'):
                    exited = trade['exit_time']
                    if exited.tzinfo is None:
                        exited = pytz.timezone('US/Eastern').localize(exited)
                    duration = exited - created
                    trade['duration_seconds'] = int(duration.total_seconds())
                    trade['duration_display'] = _format_duration(duration)
            
            completed_trades.append(trade)
        
        logger.info(f"Found {len(completed_trades)} completed trades")
        return completed_trades
        
    except Exception as e:
        logger.error(f"Error getting completed trades: {e}", exc_info=True)
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
