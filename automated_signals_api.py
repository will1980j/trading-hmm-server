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
            
            # Get active trades from signal_lab_v2_trades
            cursor.execute("""
                SELECT 
                    id,
                    date,
                    time,
                    bias,
                    entry_price,
                    stop_loss_price,
                    current_mfe,
                    session,
                    created_at,
                    trade_status
                FROM signal_lab_v2_trades
                WHERE trade_status IN ('ACTIVE', 'CONFIRMED')
                ORDER BY created_at DESC
            """)
            active_trades = [dict(row) for row in cursor.fetchall()]
            
            # Calculate duration for active trades
            now = datetime.now(pytz.timezone('US/Eastern'))
            for trade in active_trades:
                if trade['created_at']:
                    created = trade['created_at']
                    if created.tzinfo is None:
                        created = pytz.timezone('US/Eastern').localize(created)
                    duration = now - created
                    trade['duration_seconds'] = int(duration.total_seconds())
                    trade['duration_display'] = format_duration(duration)
                else:
                    trade['duration_seconds'] = 0
                    trade['duration_display'] = '0m 0s'
            
            # Get completed trades from today
            today = datetime.now(pytz.timezone('US/Eastern')).date()
            cursor.execute("""
                SELECT 
                    id,
                    date,
                    time,
                    bias,
                    entry_price,
                    stop_loss_price,
                    final_mfe,
                    session,
                    created_at,
                    trade_status
                FROM signal_lab_v2_trades
                WHERE trade_status = 'RESOLVED'
                AND date = %s
                ORDER BY created_at DESC
                LIMIT 50
            """, (today,))
            completed_trades = [dict(row) for row in cursor.fetchall()]
            
            # Get today's statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_signals,
                    COUNT(CASE WHEN trade_status IN ('ACTIVE', 'CONFIRMED') THEN 1 END) as active_count,
                    COUNT(CASE WHEN trade_status = 'RESOLVED' THEN 1 END) as completed_count,
                    AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe END) as avg_mfe,
                    COUNT(CASE WHEN final_mfe >= 1.0 THEN 1 END) as win_count
                FROM signal_lab_v2_trades
                WHERE date = %s
            """, (today,))
            stats = dict(cursor.fetchone())
            
            # Calculate win rate
            if stats['completed_count'] and stats['completed_count'] > 0:
                stats['win_rate'] = (stats['win_count'] / stats['completed_count']) * 100
            else:
                stats['win_rate'] = 0
            
            # Get hourly distribution for calendar heatmap
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM time) as hour,
                    COUNT(*) as count,
                    AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe 
                             WHEN current_mfe IS NOT NULL THEN current_mfe END) as avg_mfe,
                    COUNT(CASE WHEN trade_status IN ('ACTIVE', 'CONFIRMED') THEN 1 END) as active,
                    COUNT(CASE WHEN trade_status = 'RESOLVED' THEN 1 END) as completed
                FROM signal_lab_v2_trades
                WHERE date = %s
                GROUP BY EXTRACT(HOUR FROM time)
                ORDER BY hour
            """, (today,))
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
                    COUNT(*) as count,
                    AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe 
                             WHEN current_mfe IS NOT NULL THEN current_mfe END) as avg_mfe
                FROM signal_lab_v2_trades
                WHERE date = %s
                GROUP BY session
            """, (today,))
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
                FROM signal_lab_v2_trades
                WHERE final_mfe IS NOT NULL
                AND trade_status = 'RESOLVED'
                AND date >= CURRENT_DATE - INTERVAL '7 days'
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
            today = datetime.now(pytz.timezone('US/Eastern')).date()
            
            # Get today's statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_signals,
                    COUNT(CASE WHEN trade_status IN ('ACTIVE', 'CONFIRMED') THEN 1 END) as active_count,
                    COUNT(CASE WHEN trade_status = 'PENDING' THEN 1 END) as pending_count,
                    COUNT(CASE WHEN trade_status = 'RESOLVED' THEN 1 END) as completed_count,
                    AVG(CASE WHEN final_mfe IS NOT NULL THEN final_mfe 
                             WHEN current_mfe IS NOT NULL THEN current_mfe END) as avg_mfe,
                    COUNT(CASE WHEN final_mfe >= 1.0 THEN 1 END) as win_count
                FROM signal_lab_v2_trades
                WHERE date = %s
            """, (today,))
            stats = dict(cursor.fetchone())
            
            # Calculate win rate and success rate
            if stats['completed_count'] and stats['completed_count'] > 0:
                stats['win_rate'] = (stats['win_count'] / stats['completed_count']) * 100
                stats['success_rate'] = stats['win_rate']
            else:
                stats['win_rate'] = 0
                stats['success_rate'] = 0
            
            # Get session breakdown
            cursor.execute("""
                SELECT 
                    session,
                    COUNT(*) as count
                FROM signal_lab_v2_trades
                WHERE date = %s
                GROUP BY session
            """, (today,))
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
                SELECT 
                    id,
                    date,
                    time,
                    bias as direction,
                    entry_price,
                    stop_loss_price,
                    current_mfe as mfe,
                    session,
                    created_at as timestamp,
                    trade_status
                FROM signal_lab_v2_trades
                WHERE trade_status IN ('ACTIVE', 'CONFIRMED')
                ORDER BY created_at DESC
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
            today = datetime.now(pytz.timezone('US/Eastern')).date()
            
            cursor.execute("""
                SELECT 
                    id,
                    date,
                    time,
                    bias as direction,
                    entry_price,
                    stop_loss_price,
                    final_mfe as mfe,
                    session,
                    created_at as timestamp,
                    trade_status
                FROM signal_lab_v2_trades
                WHERE trade_status = 'RESOLVED'
                AND date = %s
                ORDER BY created_at DESC
                LIMIT 20
            """, (today,))
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
            today = datetime.now(pytz.timezone('US/Eastern')).date()
            
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM time) as hour,
                    COUNT(*) as count
                FROM signal_lab_v2_trades
                WHERE date = %s
                GROUP BY EXTRACT(HOUR FROM time)
                ORDER BY hour
            """, (today,))
            
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
                    date,
                    bias as direction,
                    session,
                    time,
                    COALESCE(final_mfe, current_mfe, 0) as mfe,
                    trade_status
                FROM signal_lab_v2_trades
                WHERE date >= CURRENT_DATE - INTERVAL '90 days'
                ORDER BY date DESC, time DESC
            """)
            
            trades = cursor.fetchall()
            
            # Group by date
            daily_data = {}
            for trade in trades:
                date_str = trade['date'].strftime('%Y-%m-%d')
                
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'trades': [],
                        'total_r': 0,
                        'trade_count': 0,
                        'has_news': False
                    }
                
                mfe = float(trade['mfe']) if trade['mfe'] else 0
                daily_data[date_str]['trades'].append({
                    'direction': trade['direction'],
                    'session': trade['session'],
                    'time': trade['time'].strftime('%H:%M') if trade['time'] else None,
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
