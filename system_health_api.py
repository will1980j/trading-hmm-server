"""
System Health Monitor API
Comprehensive health checks for Automated Signals system
"""

from flask import jsonify
import psycopg2
import requests
import os
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

def register_system_health_api(app, db):
    """Register system health monitoring endpoints"""
    
    @app.route('/api/system-health')
    def get_system_health():
        """
        Comprehensive system health check
        Returns status for all critical components
        """
        try:
            health_status = {
                'timestamp': datetime.now(pytz.timezone('US/Eastern')).isoformat(),
                'overall_status': 'healthy',
                'components': {}
            }
            
            # 1. DATABASE HEALTH
            db_health = check_database_health(db)
            health_status['components']['database'] = db_health
            
            # 2. WEBHOOK HEALTH
            webhook_health = check_webhook_health(db)
            health_status['components']['webhook'] = webhook_health
            
            # 3. EVENT FLOW HEALTH
            event_health = check_event_flow_health(db)
            health_status['components']['events'] = event_health
            
            # 4. DATA FRESHNESS
            freshness_health = check_data_freshness(db)
            health_status['components']['freshness'] = freshness_health
            
            # 5. API PERFORMANCE
            api_health = check_api_performance()
            health_status['components']['api'] = api_health
            
            # Determine overall status
            all_statuses = [
                db_health['status'],
                webhook_health['status'],
                event_health['status'],
                freshness_health['status'],
                api_health['status']
            ]
            
            if 'critical' in all_statuses:
                health_status['overall_status'] = 'critical'
            elif 'warning' in all_statuses:
                health_status['overall_status'] = 'warning'
            else:
                health_status['overall_status'] = 'healthy'
            
            return jsonify(health_status)
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return jsonify({
                'timestamp': datetime.now(pytz.timezone('US/Eastern')).isoformat(),
                'overall_status': 'critical',
                'error': str(e)
            }), 500


def check_database_health(db):
    """Check PostgreSQL database health"""
    try:
        cursor = db.conn.cursor()
        
        # Test connection
        cursor.execute("SELECT 1")
        
        # Check table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'automated_signals'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM automated_signals")
        row_count = cursor.fetchone()[0]
        
        # Check for required columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals'
            AND column_name IN ('be_mfe', 'no_be_mfe', 'signal_date', 'signal_time')
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        # Query performance test
        start_time = datetime.now()
        cursor.execute("SELECT * FROM automated_signals LIMIT 10")
        cursor.fetchall()
        query_time = (datetime.now() - start_time).total_seconds() * 1000
        
        status = 'healthy'
        issues = []
        
        if not table_exists:
            status = 'critical'
            issues.append('Table automated_signals does not exist')
        
        if len(columns) < 4:
            status = 'warning'
            issues.append(f'Missing columns: {4 - len(columns)}')
        
        if query_time > 2000:
            status = 'warning'
            issues.append(f'Slow queries: {query_time:.0f}ms')
        
        return {
            'status': status,
            'connected': True,
            'table_exists': table_exists,
            'row_count': row_count,
            'query_time_ms': round(query_time, 0),
            'columns_ok': len(columns) == 4,
            'issues': issues
        }
        
    except Exception as e:
        return {
            'status': 'critical',
            'connected': False,
            'error': str(e),
            'issues': ['Database connection failed']
        }


def check_webhook_health(db):
    """Check webhook reception health"""
    try:
        cursor = db.conn.cursor()
        
        # Check last webhook received
        cursor.execute("""
            SELECT MAX(timestamp) as last_webhook
            FROM automated_signals
            WHERE timestamp >= NOW() - INTERVAL '10 minutes'
        """)
        last_webhook = cursor.fetchone()[0]
        
        # Count webhooks in last hour
        cursor.execute("""
            SELECT COUNT(*) 
            FROM automated_signals
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
        """)
        webhooks_last_hour = cursor.fetchone()[0]
        
        # Check for each event type in last hour
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM automated_signals
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            GROUP BY event_type
        """)
        event_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        status = 'healthy'
        issues = []
        
        if last_webhook:
            seconds_since = (datetime.now(pytz.UTC) - last_webhook.replace(tzinfo=pytz.UTC)).total_seconds()
            if seconds_since > 300:  # 5 minutes
                status = 'warning'
                issues.append(f'No webhooks for {int(seconds_since/60)} minutes')
        else:
            status = 'critical'
            issues.append('No webhooks received in last 10 minutes')
        
        # Check for MFE_UPDATE events
        if event_counts.get('MFE_UPDATE', 0) == 0:
            status = 'warning'
            issues.append('No MFE_UPDATE events in last hour')
        
        return {
            'status': status,
            'last_webhook_seconds_ago': int(seconds_since) if last_webhook else None,
            'webhooks_last_hour': webhooks_last_hour,
            'event_types': event_counts,
            'issues': issues
        }
        
    except Exception as e:
        return {
            'status': 'critical',
            'error': str(e),
            'issues': ['Webhook health check failed']
        }


def check_event_flow_health(db):
    """Check event flow and lifecycle completeness"""
    try:
        cursor = db.conn.cursor()
        
        # Count active trades
        cursor.execute("""
            SELECT COUNT(DISTINCT trade_id)
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND trade_id NOT IN (
                SELECT trade_id FROM automated_signals 
                WHERE event_type LIKE 'EXIT_%'
            )
        """)
        active_trades = cursor.fetchone()[0]
        
        # Count active trades with MFE updates
        cursor.execute("""
            SELECT COUNT(DISTINCT e.trade_id)
            FROM automated_signals e
            WHERE e.event_type = 'ENTRY'
            AND e.trade_id NOT IN (
                SELECT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
            )
            AND EXISTS (
                SELECT 1 FROM automated_signals m
                WHERE m.trade_id = e.trade_id
                AND m.event_type = 'MFE_UPDATE'
            )
        """)
        trades_with_mfe = cursor.fetchone()[0]
        
        # Count completed trades today
        cursor.execute("""
            SELECT COUNT(DISTINCT trade_id)
            FROM automated_signals
            WHERE event_type LIKE 'EXIT_%'
            AND DATE(timestamp) = CURRENT_DATE
        """)
        completed_today = cursor.fetchone()[0]
        
        status = 'healthy'
        issues = []
        
        if active_trades > 0:
            mfe_coverage = (trades_with_mfe / active_trades) * 100
            if mfe_coverage < 80:
                status = 'warning'
                issues.append(f'Only {mfe_coverage:.0f}% of trades have MFE updates')
        
        return {
            'status': status,
            'active_trades': active_trades,
            'trades_with_mfe': trades_with_mfe,
            'mfe_coverage_percent': round((trades_with_mfe / active_trades * 100) if active_trades > 0 else 0, 1),
            'completed_today': completed_today,
            'issues': issues
        }
        
    except Exception as e:
        return {
            'status': 'critical',
            'error': str(e),
            'issues': ['Event flow check failed']
        }


def check_data_freshness(db):
    """Check data freshness and update frequency"""
    try:
        cursor = db.conn.cursor()
        
        # Check most recent MFE update
        cursor.execute("""
            SELECT MAX(timestamp) as last_mfe
            FROM automated_signals
            WHERE event_type = 'MFE_UPDATE'
        """)
        last_mfe = cursor.fetchone()[0]
        
        # Check most recent ENTRY
        cursor.execute("""
            SELECT MAX(timestamp) as last_entry
            FROM automated_signals
            WHERE event_type = 'ENTRY'
        """)
        last_entry = cursor.fetchone()[0]
        
        status = 'healthy'
        issues = []
        
        if last_mfe:
            mfe_age_seconds = (datetime.now(pytz.UTC) - last_mfe.replace(tzinfo=pytz.UTC)).total_seconds()
            if mfe_age_seconds > 120:  # 2 minutes
                status = 'warning'
                issues.append(f'MFE updates stale ({int(mfe_age_seconds/60)} min old)')
        
        return {
            'status': status,
            'last_mfe_seconds_ago': int(mfe_age_seconds) if last_mfe else None,
            'last_entry_seconds_ago': int((datetime.now(pytz.UTC) - last_entry.replace(tzinfo=pytz.UTC)).total_seconds()) if last_entry else None,
            'issues': issues
        }
        
    except Exception as e:
        return {
            'status': 'critical',
            'error': str(e),
            'issues': ['Data freshness check failed']
        }


def check_api_performance():
    """Check API endpoint performance"""
    try:
        # Test dashboard data endpoint
        start_time = datetime.now()
        response = requests.get('http://localhost:5000/api/automated-signals/dashboard-data', timeout=5)
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        status = 'healthy'
        issues = []
        
        if response.status_code != 200:
            status = 'critical'
            issues.append(f'API returned {response.status_code}')
        
        if response_time > 2000:
            status = 'warning'
            issues.append(f'Slow API response: {response_time:.0f}ms')
        
        return {
            'status': status,
            'response_time_ms': round(response_time, 0),
            'status_code': response.status_code,
            'issues': issues
        }
        
    except requests.Timeout:
        return {
            'status': 'critical',
            'error': 'API timeout',
            'issues': ['API response timeout (>5s)']
        }
    except Exception as e:
        return {
            'status': 'warning',
            'error': str(e),
            'issues': ['API performance check failed']
        }
