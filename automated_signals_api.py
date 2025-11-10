"""
Automated Signals Dashboard API
Provides real data endpoints for the Trading Floor Command Center
NO FAKE DATA - All data comes from actual database queries
"""

from flask import jsonify
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

def register_automated_signals_api(app, db):
    """Register all API endpoints for automated signals dashboard"""
    
    @app.route('/api/automated-signals/dashboard-data')
    def get_dashboard_data():
        """Get complete dashboard data - active trades, completed trades, stats"""
        try:
            cursor = db.conn.cursor()
            
            # Get active trades from automated_signals table (ENTRY events without EXIT)
            cursor.execute("""
                SELECT DISTINCT ON (trade_id)
                    id,
                    trade_id,
                    direction as bias,
                    CAST(entry_price AS FLOAT) as entry_price,
                    CAST(stop_loss AS FLOAT) as stop_loss_price,
                    CAST(mfe AS FLOAT) as current_mfe,
                    session,
                    timestamp as created_at,
                    'ACTIVE' as trade_status
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND trade_id NOT IN (
                    SELECT trade_id FROM automated_signals 
                    WHERE event_type LIKE 'EXIT_%'
                )
                ORDER BY trade_id, timestamp DESC
            """)
            active_trades = []
            for row in cursor.fetchall():
                trade = dict(row)
                # Ensure all numeric fields are floats
                if trade.get('entry_price'):
                    trade['entry_price'] = float(trade['entry_price'])
                if trade.get('stop_loss_price'):
                    trade['stop_loss_price'] = float(trade['stop_loss_price'])
                if trade.get('current_mfe'):
                    trade['current_mfe'] = float(trade['current_mfe'])
                active_trades.append(trade)
            
            # Calculate duration for active trades
            now = datetime.now(pytz.timezone('US/Eastern'))
            for trade in active_trades:
                if trade.get('created_at'):
                    created = trade['created_at']
                    if created.tzinfo is None:
                        created = pytz.timezone('US/Eastern').localize(created)
                    duration = now - created
                    trade['duration_seconds'] = int(duration.total_seconds())
                    trade['duration_display'] = format_duration(duration)
                else:
                    trade['duration_seconds'] = 0
                    trade['duration_display'] = '0m 0s'
            
            # Get completed trades (trades with EXIT events)
            cursor.execute("""
                SELECT 
                    e.id,
                    e.trade_id,
                    e.direction as bias,
                    CAST(e.entry_price AS FLOAT) as entry_price,
                    CAST(e.stop_loss AS FLOAT) as stop_loss_price,
                    CAST(x.final_mfe AS FLOAT) as final_mfe,
                    e.session,
                    e.timestamp as created_at,
                    'RESOLVED' as trade_status
                FROM automated_signals e
                INNER JOIN (
                    SELECT trade_id, final_mfe, timestamp
                    FROM automated_signals
                    WHERE event_type LIKE 'EXIT_%'
                ) x ON e.trade_id = x.trade_id
                WHERE e.event_type = 'ENTRY'
                AND DATE(e.timestamp) = CURRENT_DATE
                ORDER BY e.timestamp DESC
                LIMIT 50
            """)
            completed_trades = []
            for row in cursor.fetchall():
                trade = dict(row)
                # Ensure all numeric fields are floats
                if trade.get('entry_price'):
                    trade['entry_price'] = float(trade['entry_price'])
                if trade.get('stop_loss_price'):
                    trade['stop_loss_price'] = float(trade['stop_loss_price'])
                if trade.get('final_mfe'):
                    trade['final_mfe'] = float(trade['final_mfe'])
                completed_trades.append(trade)
            
            # Get today's statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT CASE WHEN event_type = 'ENTRY' THEN trade_id END) as total_signals,
                    COUNT(DISTINCT CASE WHEN event_type = 'ENTRY' 
                        AND trade_id NOT IN (SELECT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
                        THEN trade_id END) as active_count,
                    COUNT(DISTINCT CASE WHEN event_type LIKE 'EXIT_%' THEN trade_id END) as completed_count,
                    CAST(AVG(CASE WHEN event_type LIKE 'EXIT_%' THEN final_mfe END) AS FLOAT) as avg_mfe,
                    COUNT(DISTINCT CASE WHEN event_type LIKE 'EXIT_%' AND final_mfe >= 1.0 THEN trade_id END) as win_count
                FROM automated_signals
                WHERE DATE(timestamp) = CURRENT_DATE
            """)
            stats_row = cursor.fetchone()
            stats = dict(stats_row) if stats_row else {
                'total_signals': 0,
                'active_count': 0,
                'completed_count': 0,
                'avg_mfe': 0.0,
                'win_count': 0
            }
            
            # Convert to proper types
            stats['total_signals'] = int(stats['total_signals']) if stats['total_signals'] else 0
            stats['active_count'] = int(stats['active_count']) if stats['active_count'] else 0
            stats['completed_count'] = int(stats['completed_count']) if stats['completed_count'] else 0
            stats['avg_mfe'] = float(stats['avg_mfe']) if stats['avg_mfe'] else 0.0
            stats['win_count'] = int(stats['win_count']) if stats['win_count'] else 0
            
            # Calculate win rate
            if stats['completed_count'] and stats['completed_count'] > 0:
                stats['win_rate'] = (stats['win_count'] / stats['completed_count']) * 100
            else:
                stats['win_rate'] = 0
            
            # Get hourly distribution for calendar heatmap
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM timestamp) as hour,
                    COUNT(DISTINCT trade_id) as count,
                    AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe 
                             WHEN mfe IS NOT NULL THEN mfe END) as avg_mfe,
                    COUNT(DISTINCT CASE WHEN event_type = 'ENTRY' 
                        AND trade_id NOT IN (SELECT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
                        THEN trade_id END) as active,
                    COUNT(DISTINCT CASE WHEN event_type LIKE 'EXIT_%' THEN trade_id END) as completed
                FROM automated_signals
                WHERE DATE(timestamp) = CURRENT_DATE
                GROUP BY EXTRACT(HOUR FROM timestamp)
                ORDER BY hour
            """)
            hourly_data = {}
            for row in cursor.fetchall():
                hour = int(row['hour'])
                hourly_data[hour] = {
                    'count': row['count'],
                    'avg_mfe': float(row['avg_mfe']) if row['avg_mfe'] else 0,
                    'active': row['active'],
                    'completed': row['completed']
                }
            
            # Get session breakdown
            cursor.execute("""
                SELECT 
                    session,
                    COUNT(DISTINCT trade_id) as count,
                    AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe 
                             WHEN mfe IS NOT NULL THEN mfe END) as avg_mfe
                FROM automated_signals
                WHERE DATE(timestamp) = CURRENT_DATE
                AND session IS NOT NULL
                GROUP BY session
            """)
            session_breakdown = {}
            for row in cursor.fetchall():
                session_breakdown[row['session']] = {
                    'count': row['count'],
                    'avg_mfe': float(row['avg_mfe']) if row['avg_mfe'] else 0
                }
            
            return jsonify({
                'success': True,
                'active_trades': active_trades,
                'completed_trades': completed_trades,
                'stats': stats,
                'hourly_distribution': hourly_data,
                'session_breakdown': session_breakdown,
                'timestamp': datetime.now(pytz.timezone('US/Eastern')).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/automated-signals/mfe-distribution')
    def get_mfe_distribution():
        """Get MFE distribution for histogram"""
        try:
            cursor = db.conn.cursor()
            
            # Get MFE values from completed trades
            cursor.execute("""
                SELECT final_mfe as mfe
                FROM automated_signals
                WHERE final_mfe IS NOT NULL
                AND event_type LIKE 'EXIT_%'
                AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY final_mfe
            """)
            
            mfe_values = [float(row['mfe']) for row in cursor.fetchall()]
            
            # Create distribution buckets
            buckets = {
                '0-0.5R': 0,
                '0.5-1R': 0,
                '1-1.5R': 0,
                '1.5-2R': 0,
                '2-2.5R': 0,
                '2.5-3R': 0,
                '3R+': 0
            }
            
            for mfe in mfe_values:
                if mfe < 0.5:
                    buckets['0-0.5R'] += 1
                elif mfe < 1.0:
                    buckets['0.5-1R'] += 1
                elif mfe < 1.5:
                    buckets['1-1.5R'] += 1
                elif mfe < 2.0:
                    buckets['1.5-2R'] += 1
                elif mfe < 2.5:
                    buckets['2-2.5R'] += 1
                elif mfe < 3.0:
                    buckets['2.5-3R'] += 1
                else:
                    buckets['3R+'] += 1
            
            return jsonify({
                'success': True,
                'distribution': buckets,
                'raw_values': mfe_values
            })
            
        except Exception as e:
            logger.error(f"Error fetching MFE distribution: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/automated-signals/stats')
    def get_stats():
        """Get dashboard statistics"""
        try:
            cursor = db.conn.cursor()
            
            # Get today's statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT CASE WHEN event_type = 'ENTRY' THEN trade_id END) as total_signals,
                    COUNT(DISTINCT CASE WHEN event_type = 'ENTRY' 
                        AND trade_id NOT IN (SELECT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
                        THEN trade_id END) as active_count,
                    0 as pending_count,
                    COUNT(DISTINCT CASE WHEN event_type LIKE 'EXIT_%' THEN trade_id END) as completed_count,
                    CAST(AVG(CASE WHEN event_type LIKE 'EXIT_%' THEN final_mfe 
                             WHEN event_type = 'MFE_UPDATE' THEN mfe END) AS FLOAT) as avg_mfe,
                    COUNT(DISTINCT CASE WHEN event_type LIKE 'EXIT_%' AND final_mfe >= 1.0 THEN trade_id END) as win_count
                FROM automated_signals
                WHERE DATE(timestamp) = CURRENT_DATE
            """)
            stats_row = cursor.fetchone()
            stats = dict(stats_row) if stats_row else {
                'total_signals': 0,
                'active_count': 0,
                'pending_count': 0,
                'completed_count': 0,
                'avg_mfe': 0.0,
                'win_count': 0
            }
            
            # Convert to proper types
            stats['total_signals'] = int(stats['total_signals']) if stats['total_signals'] else 0
            stats['active_count'] = int(stats['active_count']) if stats['active_count'] else 0
            stats['pending_count'] = 0
            stats['completed_count'] = int(stats['completed_count']) if stats['completed_count'] else 0
            stats['avg_mfe'] = float(stats['avg_mfe']) if stats['avg_mfe'] else 0.0
            stats['win_count'] = int(stats['win_count']) if stats['win_count'] else 0
            
            # Calculate win rate and success rate
            if stats['completed_count'] > 0:
                stats['win_rate'] = float((stats['win_count'] / stats['completed_count']) * 100)
                stats['success_rate'] = stats['win_rate']
            else:
                stats['win_rate'] = 0.0
                stats['success_rate'] = 0.0
            
            # Get session breakdown
            cursor.execute("""
                SELECT 
                    session,
                    COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE DATE(timestamp) = CURRENT_DATE
                AND session IS NOT NULL
                GROUP BY session
            """)
            session_breakdown = {}
            for row in cursor.fetchall():
                session_breakdown[row['session']] = row['count']
            
            return jsonify({
                'success': True,
                'total_signals': stats['total_signals'] or 0,
                'active_count': stats['active_count'] or 0,
                'pending_count': stats['pending_count'] or 0,
                'completed_count': stats['completed_count'] or 0,
                'avg_mfe': float(stats['avg_mfe']) if stats['avg_mfe'] else 0,
                'win_rate': stats['win_rate'],
                'success_rate': stats['success_rate'],
                'session_breakdown': session_breakdown
            })
            
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/automated-signals/active')
    def get_active_trades():
        """Get active trades"""
        try:
            cursor = db.conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT ON (trade_id)
                    id,
                    trade_id,
                    direction,
                    entry_price,
                    stop_loss as stop_loss_price,
                    mfe,
                    session,
                    timestamp,
                    'ACTIVE' as trade_status
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND trade_id NOT IN (
                    SELECT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
                )
                ORDER BY trade_id, timestamp DESC
            """)
            trades = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'trades': trades
            })
            
        except Exception as e:
            logger.error(f"Error fetching active trades: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/automated-signals/completed')
    def get_completed_trades():
        """Get completed trades"""
        try:
            cursor = db.conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.id,
                    e.trade_id,
                    e.direction,
                    e.entry_price,
                    e.stop_loss as stop_loss_price,
                    x.final_mfe as mfe,
                    e.session,
                    e.timestamp,
                    'RESOLVED' as trade_status
                FROM automated_signals e
                INNER JOIN (
                    SELECT trade_id, final_mfe, timestamp
                    FROM automated_signals
                    WHERE event_type LIKE 'EXIT_%'
                ) x ON e.trade_id = x.trade_id
                WHERE e.event_type = 'ENTRY'
                AND DATE(e.timestamp) = CURRENT_DATE
                ORDER BY e.timestamp DESC
                LIMIT 20
            """)
            trades = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'trades': trades
            })
            
        except Exception as e:
            logger.error(f"Error fetching completed trades: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/automated-signals/hourly-distribution')
    def get_hourly_distribution():
        """Get hourly trade distribution for calendar heatmap"""
        try:
            cursor = db.conn.cursor()
            
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM timestamp) as hour,
                    COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE DATE(timestamp) = CURRENT_DATE
                AND event_type = 'ENTRY'
                GROUP BY EXTRACT(HOUR FROM timestamp)
                ORDER BY hour
            """)
            
            hourly_data = {}
            for row in cursor.fetchall():
                hour = int(row['hour'])
                hourly_data[hour] = row['count']
            
            return jsonify({
                'success': True,
                'hourly_data': hourly_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching hourly distribution: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/automated-signals/daily-calendar')
    def get_daily_calendar():
        """Get daily trade data for full calendar view"""
        try:
            cursor = db.conn.cursor()
            
            # Get all trades grouped by date
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    direction,
                    session,
                    timestamp::time as time,
                    COALESCE(final_mfe, mfe, 0) as mfe,
                    CASE 
                        WHEN event_type LIKE 'EXIT_%' THEN 'RESOLVED'
                        WHEN event_type = 'ENTRY' THEN 'ACTIVE'
                        ELSE 'PENDING'
                    END as trade_status
                FROM automated_signals
                WHERE timestamp >= CURRENT_DATE - INTERVAL '90 days'
                AND event_type IN ('ENTRY', 'EXIT_STOP_LOSS', 'EXIT_BREAK_EVEN')
                ORDER BY timestamp DESC
            """)
            
            trades = cursor.fetchall()
            
            # Group by date
            daily_data = {}
            for trade in trades:
                date_str = trade['date'].strftime('%Y-%m-%d') if hasattr(trade['date'], 'strftime') else str(trade['date'])
                
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'trades': [],
                        'total_r': 0,
                        'trade_count': 0,
                        'has_news': False
                    }
                
                mfe = float(trade['mfe']) if trade['mfe'] else 0
                time_str = trade['time'].strftime('%H:%M') if hasattr(trade['time'], 'strftime') else str(trade['time'])[:5] if trade['time'] else None
                daily_data[date_str]['trades'].append({
                    'direction': trade['direction'],
                    'session': trade['session'],
                    'time': time_str,
                    'mfe': mfe
                })
                daily_data[date_str]['total_r'] += mfe
                daily_data[date_str]['trade_count'] += 1
            
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

def format_duration(duration):
    """Format timedelta to readable string"""
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
