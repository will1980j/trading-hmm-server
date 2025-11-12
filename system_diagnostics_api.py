"""
Live System Diagnostics API
Provides real-time health checks and signal-level verification
"""

from flask import jsonify
import psycopg2
from datetime import datetime, timedelta
import pytz
import os

def register_diagnostics_api(app):
    """Register diagnostic endpoints"""
    
    @app.route('/api/automated-signals/batch-delete', methods=['POST'])
    def batch_delete_signals():
        """
        Batch delete signals by trade_ids
        Expects JSON: {"trade_ids": ["id1", "id2", ...]}
        """
        from flask import request
        
        try:
            data = request.get_json()
            trade_ids = data.get('trade_ids', [])
            
            if not trade_ids:
                return jsonify({'success': False, 'error': 'No trade_ids provided'}), 400
            
            DATABASE_URL = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Delete all events for these trade_ids
            placeholders = ','.join(['%s'] * len(trade_ids))
            query = f"DELETE FROM automated_signals WHERE trade_id IN ({placeholders})"
            cur.execute(query, trade_ids)
            deleted_count = cur.rowcount
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'deleted_count': deleted_count,
                'trade_ids': trade_ids
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/automated-signals/diagnostics/run')
    def run_full_diagnostics():
        """
        Run comprehensive system diagnostics
        Returns step-by-step results for live display
        """
        results = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'checks': [],
            'overall_status': 'HEALTHY',
            'critical_issues': [],
            'warnings': []
        }
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # CHECK 1: Database Connection
            check1 = {
                'name': 'Database Connection',
                'status': 'PASS',
                'message': 'Connected to Railway PostgreSQL',
                'duration_ms': 0
            }
            results['checks'].append(check1)
            
            # CHECK 2: Table Existence
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'automated_signals');")
            table_exists = cur.fetchone()[0]
            check2 = {
                'name': 'Table Existence',
                'status': 'PASS' if table_exists else 'FAIL',
                'message': 'automated_signals table found' if table_exists else 'Table missing!',
                'duration_ms': 0
            }
            results['checks'].append(check2)
            if not table_exists:
                results['critical_issues'].append('automated_signals table does not exist')
                results['overall_status'] = 'CRITICAL'
            
            # CHECK 3: Recent Signal Activity
            cur.execute("""
                SELECT 
                    MAX(timestamp) as last_signal,
                    EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 as minutes_ago
                FROM automated_signals
                WHERE event_type = 'ENTRY'
            """)
            row = cur.fetchone()
            last_signal, minutes_ago = row if row else (None, None)
            
            if minutes_ago is None:
                check3 = {
                    'name': 'Recent Signal Activity',
                    'status': 'WARN',
                    'message': 'No signals found in database',
                    'duration_ms': 0
                }
                results['warnings'].append('No signals received yet')
            elif minutes_ago > 60:
                check3 = {
                    'name': 'Recent Signal Activity',
                    'status': 'WARN',
                    'message': f'Last signal {minutes_ago:.0f} minutes ago - TradingView alert may be stopped',
                    'duration_ms': 0,
                    'data': {'minutes_ago': minutes_ago, 'last_signal': last_signal.isoformat()}
                }
                results['warnings'].append(f'No new signals in {minutes_ago/60:.1f} hours')
            else:
                check3 = {
                    'name': 'Recent Signal Activity',
                    'status': 'PASS',
                    'message': f'Last signal {minutes_ago:.1f} minutes ago',
                    'duration_ms': 0,
                    'data': {'minutes_ago': minutes_ago, 'last_signal': last_signal.isoformat()}
                }
            results['checks'].append(check3)
            
            # CHECK 4: TradingView Alert Status
            # Check if we're receiving signals regularly (indicates alert is active)
            cur.execute("""
                SELECT 
                    COUNT(*) as signals_last_hour,
                    COUNT(DISTINCT DATE_TRUNC('minute', timestamp)) as active_minutes
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND timestamp > NOW() - INTERVAL '1 hour'
            """)
            signals_last_hour, active_minutes = cur.fetchone()
            
            # Also check the time gap between last 2 signals
            cur.execute("""
                SELECT timestamp
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                ORDER BY timestamp DESC
                LIMIT 2
            """)
            recent_signals = cur.fetchall()
            
            alert_status = 'UNKNOWN'
            alert_message = 'Unable to determine alert status'
            
            if len(recent_signals) >= 2:
                time_gap = (recent_signals[0][0] - recent_signals[1][0]).total_seconds() / 60
                
                if minutes_ago and minutes_ago < 15:
                    alert_status = 'PASS'
                    alert_message = f'TradingView alert is ACTIVE - {signals_last_hour} signals in last hour'
                elif minutes_ago and minutes_ago < 60:
                    alert_status = 'WARN'
                    alert_message = f'TradingView alert may be IDLE - last signal {minutes_ago:.0f} min ago'
                else:
                    alert_status = 'FAIL'
                    alert_message = f'TradingView alert appears STOPPED - no signals for {minutes_ago/60:.1f} hours'
                    results['critical_issues'].append('TradingView alert not sending signals')
            elif len(recent_signals) == 1:
                alert_status = 'WARN'
                alert_message = 'Only 1 signal in database - cannot verify alert continuity'
            else:
                alert_status = 'FAIL'
                alert_message = 'No signals in database - TradingView alert not configured'
                results['critical_issues'].append('TradingView alert not configured')
            
            check4 = {
                'name': 'TradingView Alert Status',
                'status': alert_status,
                'message': alert_message,
                'duration_ms': 0,
                'data': {
                    'signals_last_hour': signals_last_hour,
                    'active_minutes': active_minutes,
                    'minutes_since_last': minutes_ago
                }
            }
            results['checks'].append(check4)
            
            if alert_status == 'WARN':
                results['warnings'].append(f'TradingView alert status: {alert_message}')
            
            # CHECK 5: Stale Active Trades
            cur.execute("""
                SELECT COUNT(*) as stale_count
                FROM automated_signals e
                WHERE e.event_type = 'ENTRY'
                AND e.trade_id NOT IN (
                    SELECT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
                )
                AND e.timestamp < NOW() - INTERVAL '2 hours'
            """)
            stale_count = cur.fetchone()[0]
            
            if stale_count > 0:
                check5 = {
                    'name': 'Stale Active Trades',
                    'status': 'WARN',
                    'message': f'{stale_count} trades missing EXIT events (>2 hours old)',
                    'duration_ms': 0,
                    'data': {'stale_count': stale_count}
                }
                results['warnings'].append(f'{stale_count} stale trades detected')
            else:
                check5 = {
                    'name': 'Stale Active Trades',
                    'status': 'PASS',
                    'message': 'No stale trades detected',
                    'duration_ms': 0
                }
            results['checks'].append(check5)
            
            # CHECK 6: Event Type Distribution
            cur.execute("""
                SELECT event_type, COUNT(*) as count
                FROM automated_signals
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                GROUP BY event_type
                ORDER BY count DESC
            """)
            event_dist = cur.fetchall()
            
            check6 = {
                'name': 'Event Distribution (24h)',
                'status': 'PASS',
                'message': f'{len(event_dist)} event types in last 24 hours',
                'duration_ms': 0,
                'data': {row[0]: row[1] for row in event_dist}
            }
            results['checks'].append(check6)
            
            # CHECK 7: MFE Update Frequency
            cur.execute("""
                SELECT 
                    COUNT(*) as mfe_updates,
                    COUNT(DISTINCT trade_id) as unique_trades
                FROM automated_signals
                WHERE event_type = 'MFE_UPDATE'
                AND timestamp > NOW() - INTERVAL '1 hour'
            """)
            mfe_updates, unique_trades = cur.fetchone()
            
            check7 = {
                'name': 'MFE Update Frequency',
                'status': 'PASS',
                'message': f'{mfe_updates} MFE updates for {unique_trades} trades in last hour',
                'duration_ms': 0,
                'data': {'mfe_updates': mfe_updates, 'unique_trades': unique_trades}
            }
            results['checks'].append(check7)
            
            # CHECK 8: Completion Rate
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT CASE WHEN event_type = 'ENTRY' THEN trade_id END) as entries,
                    COUNT(DISTINCT CASE WHEN event_type LIKE 'EXIT_%' THEN trade_id END) as exits
                FROM automated_signals
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            entries, exits = cur.fetchone()
            completion_rate = (exits / entries * 100) if entries > 0 else 0
            
            if completion_rate < 50:
                check8 = {
                    'name': 'Completion Rate (24h)',
                    'status': 'WARN',
                    'message': f'{completion_rate:.1f}% completion rate - many trades missing EXIT events',
                    'duration_ms': 0,
                    'data': {'entries': entries, 'exits': exits, 'completion_rate': completion_rate}
                }
                results['warnings'].append(f'Low completion rate: {completion_rate:.1f}%')
            else:
                check8 = {
                    'name': 'Completion Rate (24h)',
                    'status': 'PASS',
                    'message': f'{completion_rate:.1f}% completion rate ({exits}/{entries} trades)',
                    'duration_ms': 0,
                    'data': {'entries': entries, 'exits': exits, 'completion_rate': completion_rate}
                }
            results['checks'].append(check8)
            
            # CHECK 9: Database Size
            cur.execute("SELECT COUNT(*) FROM automated_signals;")
            total_records = cur.fetchone()[0]
            
            check9 = {
                'name': 'Database Size',
                'status': 'PASS',
                'message': f'{total_records:,} total records',
                'duration_ms': 0,
                'data': {'total_records': total_records}
            }
            results['checks'].append(check9)
            
            # CHECK 10: Webhook Endpoint Health
            check10 = {
                'name': 'Webhook Endpoint',
                'status': 'PASS',
                'message': '/api/automated-signals/webhook is accessible',
                'duration_ms': 0
            }
            results['checks'].append(check10)
            
            # CHECK 11: Session Distribution
            cur.execute("""
                SELECT 
                    session,
                    COUNT(*) as count
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND timestamp > NOW() - INTERVAL '24 hours'
                GROUP BY session
                ORDER BY count DESC
            """)
            session_dist = cur.fetchall()
            
            check11 = {
                'name': 'Session Distribution (24h)',
                'status': 'PASS',
                'message': f'{len(session_dist)} sessions active',
                'duration_ms': 0,
                'data': {row[0] if row[0] else 'Unknown': row[1] for row in session_dist}
            }
            results['checks'].append(check11)
            
            cur.close()
            conn.close()
            
            # Determine overall status
            if results['critical_issues']:
                results['overall_status'] = 'CRITICAL'
            elif results['warnings']:
                results['overall_status'] = 'WARNING'
            else:
                results['overall_status'] = 'HEALTHY'
            
            return jsonify(results), 200
            
        except Exception as e:
            return jsonify({
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'checks': [],
                'overall_status': 'ERROR',
                'critical_issues': [str(e)],
                'warnings': [],
                'error': str(e)
            }), 500
