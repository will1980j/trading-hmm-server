"""
Signals API V2 (Phase 2A)
Lightweight read-only API endpoints for ULTRA and dashboards
Uses signal_state_builder for unified view models
NO EXECUTION, NO RISK LOGIC, NO WRITES
"""

from flask import jsonify, request
from datetime import datetime, timedelta
import pytz
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from signal_state_builder import build_signal_state, filter_active_signals, filter_completed_signals

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')


def register_signals_api_v2(app):
    """Register all Phase 2A read-only API endpoints"""
    
    @app.route('/api/signals/live', methods=['GET'])
    def get_live_signals():
        """Get all ACTIVE/PENDING/CONFIRMED signals"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all signals, group by trade_id
            cursor.execute("""
                SELECT DISTINCT ON (trade_id) *
                FROM automated_signals
                WHERE event_type NOT IN ('EXIT_SL', 'EXIT_TARGET', 'EXIT_BE', 'INVALIDATED')
                ORDER BY trade_id, timestamp DESC
                LIMIT 100
            """)
            
            rows = cursor.fetchall()
            
            # Group by trade_id
            grouped = {}
            for row in rows:
                trade_id = row['trade_id']
                if trade_id not in grouped:
                    grouped[trade_id] = []
                grouped[trade_id].append(dict(row))
            
            # Build unified states
            states = []
            for trade_id, trade_rows in grouped.items():
                # Get all rows for this trade_id
                cursor.execute("""
                    SELECT * FROM automated_signals
                    WHERE trade_id = %s
                    ORDER BY timestamp ASC
                """, (trade_id,))
                all_rows = [dict(r) for r in cursor.fetchall()]
                
                state = build_signal_state(all_rows)
                if state and state.get('status') in ['ACTIVE', 'PENDING', 'CONFIRMED']:
                    states.append(state)
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'signals': states,
                'count': len(states)
            })
            
        except Exception as e:
            logger.error(f"Error fetching live signals: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/signals/recent', methods=['GET'])
    def get_recent_signals():
        """Get N most recently COMPLETED signals"""
        try:
            limit = int(request.args.get('limit', 50))
            limit = min(limit, 500)  # Max 500
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get completed signals
            cursor.execute("""
                SELECT DISTINCT trade_id
                FROM automated_signals
                WHERE event_type IN ('EXIT_SL', 'EXIT_TARGET', 'EXIT_BE')
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            
            trade_ids = [row['trade_id'] for row in cursor.fetchall()]
            
            # Build states for each
            states = []
            for trade_id in trade_ids:
                cursor.execute("""
                    SELECT * FROM automated_signals
                    WHERE trade_id = %s
                    ORDER BY timestamp ASC
                """, (trade_id,))
                rows = [dict(r) for r in cursor.fetchall()]
                
                state = build_signal_state(rows)
                if state:
                    states.append(state)
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'signals': states,
                'count': len(states)
            })
            
        except Exception as e:
            logger.error(f"Error fetching recent signals: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/signals/today', methods=['GET'])
    def get_today_signals():
        """Get all signals from today's trading session"""
        try:
            # Get today in Eastern Time
            eastern = pytz.timezone('US/Eastern')
            now_et = datetime.now(eastern)
            today_start = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
            today_start_ts = int(today_start.timestamp() * 1000)
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all signals from today
            cursor.execute("""
                SELECT DISTINCT trade_id
                FROM automated_signals
                WHERE timestamp >= %s
                ORDER BY timestamp DESC
            """, (today_start_ts,))
            
            trade_ids = [row['trade_id'] for row in cursor.fetchall()]
            
            # Build states
            states = []
            for trade_id in trade_ids:
                cursor.execute("""
                    SELECT * FROM automated_signals
                    WHERE trade_id = %s
                    ORDER BY timestamp ASC
                """, (trade_id,))
                rows = [dict(r) for r in cursor.fetchall()]
                
                state = build_signal_state(rows)
                if state:
                    states.append(state)
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'signals': states,
                'count': len(states),
                'date': now_et.strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            logger.error(f"Error fetching today signals: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/signals/stats/today', methods=['GET'])
    def get_today_stats():
        """Compute real-time statistics for today"""
        try:
            # Get today's signals
            eastern = pytz.timezone('US/Eastern')
            now_et = datetime.now(eastern)
            today_start = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
            today_start_ts = int(today_start.timestamp() * 1000)
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT DISTINCT trade_id
                FROM automated_signals
                WHERE timestamp >= %s
            """, (today_start_ts,))
            
            trade_ids = [row['trade_id'] for row in cursor.fetchall()]
            
            # Build states and compute stats
            states = []
            for trade_id in trade_ids:
                cursor.execute("""
                    SELECT * FROM automated_signals
                    WHERE trade_id = %s
                    ORDER BY timestamp ASC
                """, (trade_id,))
                rows = [dict(r) for r in cursor.fetchall()]
                
                state = build_signal_state(rows)
                if state:
                    states.append(state)
            
            cursor.close()
            conn.close()
            
            # Compute statistics
            total = len(states)
            completed = len([s for s in states if s.get('status') == 'COMPLETED'])
            active = len([s for s in states if s.get('status') in ['ACTIVE', 'PENDING']])
            
            # Win rate
            completed_states = [s for s in states if s.get('status') == 'COMPLETED']
            wins = len([s for s in completed_states if (s.get('r_multiple') or 0) > 0])
            winrate = round((wins / completed) * 100, 2) if completed > 0 else 0
            
            # Average R
            r_values = [s.get('r_multiple') for s in completed_states if isinstance(s.get('r_multiple'), (int, float))]
            avg_r = round(sum(r_values) / len(r_values), 2) if r_values else 0
            
            # Expectancy
            expectancy = avg_r
            
            # Average MFE
            mfe_values = [s.get('mfe') for s in states if isinstance(s.get('mfe'), (int, float))]
            avg_mfe = round(sum(mfe_values) / len(mfe_values), 2) if mfe_values else 0
            
            # Average AE (not implemented)
            avg_ae = 0
            
            return jsonify({
                'success': True,
                'stats': {
                    'total': total,
                    'completed': completed,
                    'active': active,
                    'winrate': round(winrate, 2),
                    'avg_r': round(avg_r, 2),
                    'expectancy': round(expectancy, 2),
                    'avg_mfe': round(avg_mfe, 2),
                    'avg_ae': round(avg_ae, 2)
                },
                'date': now_et.strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            logger.error(f"Error computing today stats: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/session-summary', methods=['GET'])
    def get_session_summary():
        """Aggregate stats grouped by session"""
        try:
            # Get date range
            start_date = request.args.get('start')
            end_date = request.args.get('end')
            
            eastern = pytz.timezone('US/Eastern')
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                start_dt = eastern.localize(start_dt)
            else:
                # Default: last 30 days
                start_dt = datetime.now(eastern) - timedelta(days=30)
                start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = eastern.localize(end_dt)
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:
                end_dt = datetime.now(eastern)
            
            start_ts = int(start_dt.timestamp() * 1000)
            end_ts = int(end_dt.timestamp() * 1000)
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all signals in range
            cursor.execute("""
                SELECT DISTINCT trade_id
                FROM automated_signals
                WHERE timestamp >= %s AND timestamp <= %s
            """, (start_ts, end_ts))
            
            trade_ids = [row['trade_id'] for row in cursor.fetchall()]
            
            # Build states
            states = []
            for trade_id in trade_ids:
                cursor.execute("""
                    SELECT * FROM automated_signals
                    WHERE trade_id = %s
                    ORDER BY timestamp ASC
                """, (trade_id,))
                rows = [dict(r) for r in cursor.fetchall()]
                
                state = build_signal_state(rows)
                if state:
                    states.append(state)
            
            cursor.close()
            conn.close()
            
            # Group by session
            sessions = {}
            for state in states:
                session = state.get('session', 'UNKNOWN')
                if session not in sessions:
                    sessions[session] = []
                sessions[session].append(state)
            
            # Compute stats per session
            session_stats = {}
            for session, session_states in sessions.items():
                completed = [s for s in session_states if s.get('status') == 'COMPLETED']
                wins = len([s for s in completed if (s.get('r_multiple') or 0) > 0])
                
                r_values = [s.get('r_multiple') for s in completed if s.get('r_multiple') is not None]
                avg_r = sum(r_values) / len(r_values) if r_values else 0
                
                session_stats[session] = {
                    'total': len(session_states),
                    'completed': len(completed),
                    'wins': wins,
                    'winrate': round((wins / len(completed)) * 100, 2) if completed else 0,
                    'avg_r': round(avg_r, 2)
                }
            
            return jsonify({
                'success': True,
                'sessions': session_stats,
                'start_date': start_dt.strftime('%Y-%m-%d'),
                'end_date': end_dt.strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            logger.error(f"Error computing session summary: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/system-status', methods=['GET'])
    def get_system_status():
        """System health monitoring"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get last signal timestamp
            cursor.execute("""
                SELECT MAX(timestamp) as last_ts
                FROM automated_signals
            """)
            result = cursor.fetchone()
            last_ts = result['last_ts'] if result else None
            
            # Count active signals
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as active_count
                FROM automated_signals
                WHERE event_type NOT IN ('EXIT_SL', 'EXIT_TARGET', 'EXIT_BE', 'INVALIDATED')
            """)
            active_count = cursor.fetchone()['active_count']
            
            cursor.close()
            conn.close()
            
            # Determine webhook health
            webhook_health = 'HEALTHY'
            if last_ts:
                # Normalize last_ts into milliseconds since epoch
                now_ts_ms = datetime.now().timestamp() * 1000
                if isinstance(last_ts, datetime):
                    last_ts_ms = last_ts.timestamp() * 1000
                else:
                    last_ts_ms = float(last_ts)
                time_since_last = now_ts_ms - last_ts_ms
                if time_since_last > 3600000:  # 1 hour
                    webhook_health = 'DEGRADED'
                if time_since_last > 86400000:  # 24 hours
                    webhook_health = 'ERROR'
            
            # Get current session
            eastern = pytz.timezone('US/Eastern')
            now_et = datetime.now(eastern)
            hour = now_et.hour
            
            if 20 <= hour <= 23:
                current_session = 'ASIA'
            elif 0 <= hour <= 5:
                current_session = 'LONDON'
            elif 6 <= hour < 8 or (hour == 8 and now_et.minute < 30):
                current_session = 'NY_PRE'
            elif (hour == 8 and now_et.minute >= 30) or 9 <= hour <= 11:
                current_session = 'NY_AM'
            elif hour == 12:
                current_session = 'NY_LUNCH'
            elif 13 <= hour <= 15:
                current_session = 'NY_PM'
            else:
                current_session = 'CLOSED'
            
            return jsonify({
                'success': True,
                'status': {
                    'webhook_health': webhook_health,
                    'queue_depth': active_count,
                    'risk_engine': 'DISCONNECTED',  # Phase 3+
                    'last_signal_timestamp': last_ts,
                    'current_session': current_session,
                    'latency_ms': 50  # Mock value
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    logger.info("✅ Phase 2A API endpoints registered")
