"""
System Health Monitor API - 100% Cloud-Native
Comprehensive health checks for Automated Signals system on Railway
All checks use fresh database connections and Railway infrastructure
"""

from flask import jsonify, request
import psycopg2
import os
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

def get_fresh_db_connection():
    """Get fresh Railway PostgreSQL connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL not configured")
    return psycopg2.connect(database_url)

def register_system_health_api(app, db):
    """Register cloud-native system health monitoring endpoints"""
    
    @app.route('/api/system-health')
    def get_system_health():
        """
        Comprehensive cloud-native system health check
        Returns status for all critical Railway components
        """
        try:
            health_status = {
                'timestamp': datetime.now(pytz.timezone('US/Eastern')).isoformat(),
                'overall_status': 'healthy',
                'components': {}
            }
            
            # 1. DATABASE HEALTH (Fresh connection)
            db_health = check_database_health_fresh()
            health_status['components']['database'] = db_health
            
            # 2. WEBHOOK HEALTH (Fresh connection)
            webhook_health = check_webhook_health_fresh()
            health_status['components']['webhook'] = webhook_health
            
            # 3. EVENT FLOW HEALTH (Fresh connection)
            event_health = check_event_flow_health_fresh()
            health_status['components']['events'] = event_health
            
            # 4. DATA FRESHNESS (Fresh connection)
            freshness_health = check_data_freshness_fresh()
            health_status['components']['freshness'] = freshness_health
            
            # 5. SIGNAL INTEGRITY (Fresh connection)
            integrity_health = check_signal_integrity_fresh()
            health_status['components']['integrity'] = integrity_health
            
            # Determine overall status
            all_statuses = [
                db_health['status'],
                webhook_health['status'],
                event_health['status'],
                freshness_health['status'],
                integrity_health['status']
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


def check_database_health_fresh():
    """Check Railway PostgreSQL database health with fresh connection"""
    conn = None
    try:
        conn = get_fresh_db_connection()
        cursor = conn.cursor()
        
        # Test connection
        start_time = datetime.now()
        cursor.execute("SELECT 1")
        query_time = (datetime.now() - start_time).total_seconds() * 1000
        
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
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'critical',
            'connected': False,
            'error': str(e),
            'issues': ['Database connection failed']
        }
    finally:
        if conn:
            conn.close()


def check_webhook_health_fresh():
    """Check webhook reception health with fresh connection"""
    conn = None
    try:
        conn = get_fresh_db_connection()
        cursor = conn.cursor()
        
        # Check last webhook received
        cursor.execute("""
            SELECT MAX(timestamp) as last_webhook
            FROM automated_signals
            WHERE timestamp >= NOW() - INTERVAL '10 minutes'
        """)
        result = cursor.fetchone()
        last_webhook = result[0] if result else None
        
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
        seconds_since = None
        
        if last_webhook:
            seconds_since = (datetime.now(pytz.UTC) - last_webhook.replace(tzinfo=pytz.UTC)).total_seconds()
            if seconds_since > 300:  # 5 minutes
                status = 'warning'
                issues.append(f'No webhooks for {int(seconds_since/60)} minutes')
        else:
            status = 'critical'
            issues.append('No webhooks received in last 10 minutes')
            seconds_since = 999
        
        # Check for MFE_UPDATE events
        if event_counts.get('MFE_UPDATE', 0) == 0 and webhooks_last_hour > 0:
            status = 'warning'
            issues.append('No MFE_UPDATE events in last hour')
        
        return {
            'status': status,
            'last_webhook_seconds_ago': int(seconds_since) if seconds_since else None,
            'webhooks_last_hour': webhooks_last_hour,
            'event_types': event_counts,
            'issues': issues
        }
        
    except Exception as e:
        logger.error(f"Webhook health check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e),
            'issues': ['Webhook health check failed']
        }
    finally:
        if conn:
            conn.close()


def check_event_flow_health_fresh():
    """Check event flow and lifecycle completeness with fresh connection"""
    conn = None
    try:
        conn = get_fresh_db_connection()
        cursor = conn.cursor()
        
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
        else:
            mfe_coverage = 0
        
        return {
            'status': status,
            'active_trades': active_trades,
            'trades_with_mfe': trades_with_mfe,
            'mfe_coverage_percent': round(mfe_coverage, 1),
            'completed_today': completed_today,
            'issues': issues
        }
        
    except Exception as e:
        logger.error(f"Event flow check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e),
            'issues': ['Event flow check failed']
        }
    finally:
        if conn:
            conn.close()


def check_data_freshness_fresh():
    """Check data freshness and update frequency with fresh connection"""
    conn = None
    try:
        conn = get_fresh_db_connection()
        cursor = conn.cursor()
        
        # Check most recent MFE update
        cursor.execute("""
            SELECT MAX(timestamp) as last_mfe
            FROM automated_signals
            WHERE event_type = 'MFE_UPDATE'
        """)
        result = cursor.fetchone()
        last_mfe = result[0] if result else None
        
        # Check most recent ENTRY
        cursor.execute("""
            SELECT MAX(timestamp) as last_entry
            FROM automated_signals
            WHERE event_type = 'ENTRY'
        """)
        result = cursor.fetchone()
        last_entry = result[0] if result else None
        
        status = 'healthy'
        issues = []
        mfe_age_seconds = None
        entry_age_seconds = None
        
        if last_mfe:
            mfe_age_seconds = (datetime.now(pytz.UTC) - last_mfe.replace(tzinfo=pytz.UTC)).total_seconds()
            if mfe_age_seconds > 120:  # 2 minutes
                status = 'warning'
                issues.append(f'MFE updates stale ({int(mfe_age_seconds/60)} min old)')
        
        if last_entry:
            entry_age_seconds = (datetime.now(pytz.UTC) - last_entry.replace(tzinfo=pytz.UTC)).total_seconds()
        
        return {
            'status': status,
            'last_mfe_seconds_ago': int(mfe_age_seconds) if mfe_age_seconds else None,
            'last_entry_seconds_ago': int(entry_age_seconds) if entry_age_seconds else None,
            'issues': issues
        }
        
    except Exception as e:
        logger.error(f"Data freshness check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e),
            'issues': ['Data freshness check failed']
        }
    finally:
        if conn:
            conn.close()


def check_signal_integrity_fresh():
    """
    Randomly verify 2 signals for data integrity with fresh connection
    Compact display that expands on errors
    """
    conn = None
    try:
        conn = get_fresh_db_connection()
        cursor = conn.cursor()
        
        # Get 2 random trade IDs from last 7 days
        cursor.execute("""
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE timestamp > NOW() - INTERVAL '7 days'
            AND trade_id IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 2
        """)
        
        trade_ids = [row[0] for row in cursor.fetchall()]
        
        if not trade_ids:
            return {
                'status': 'warning',
                'signals_verified': 0,
                'errors_found': 0,
                'warnings_found': 0,
                'message': 'No signals in last 7 days',
                'issues': []
            }
        
        # Quick integrity checks on each signal
        errors = []
        warnings = []
        
        for trade_id in trade_ids:
            # Get all events for this trade
            cursor.execute("""
                SELECT event_type, be_mfe, no_be_mfe, entry_price, sl_price
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            events = cursor.fetchall()
            
            if not events:
                errors.append(f"Trade {trade_id}: No events found")
                continue
            
            # Check 1: First event should be ENTRY
            if events[0][0] != 'ENTRY':
                errors.append(f"Trade {trade_id}: First event is {events[0][0]}, not ENTRY")
            
            # Check 2: MFE values should not decrease
            prev_be_mfe = 0
            prev_no_be_mfe = 0
            for event in events:
                be_mfe = float(event[1]) if event[1] else 0
                no_be_mfe = float(event[2]) if event[2] else 0
                
                if be_mfe < prev_be_mfe - 0.01:
                    warnings.append(f"Trade {trade_id}: BE MFE decreased")
                if no_be_mfe < prev_no_be_mfe - 0.01:
                    warnings.append(f"Trade {trade_id}: No-BE MFE decreased")
                
                prev_be_mfe = max(prev_be_mfe, be_mfe)
                prev_no_be_mfe = max(prev_no_be_mfe, no_be_mfe)
        
        # Determine status
        if errors:
            status = 'critical'
        elif warnings:
            status = 'warning'
        else:
            status = 'healthy'
        
        summary = {
            'status': status,
            'signals_verified': len(trade_ids),
            'errors_found': len(errors),
            'warnings_found': len(warnings),
            'issues': (errors + warnings)[:3]  # Show first 3 issues
        }
        
        if status == 'healthy':
            summary['message'] = f"✓ {len(trade_ids)} signals verified"
        
        return summary
        
    except Exception as e:
        logger.error(f"Signal integrity check failed: {e}")
        return {
            'status': 'warning',
            'signals_verified': 0,
            'errors_found': 0,
            'warnings_found': 0,
            'error': str(e),
            'issues': ['Integrity check failed']
        }
    finally:
        if conn:
            conn.close()
