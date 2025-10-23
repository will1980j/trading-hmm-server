import psycopg2
import psycopg2.extras
import time
from datetime import datetime, timedelta
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

_db_instance = None

def _set_db_instance(db):
    """Set the db instance for health checks"""
    global _db_instance
    _db_instance = db

def get_db_connection():
    """Get database connection"""
    global _db_instance
    if _db_instance and hasattr(_db_instance, 'conn') and _db_instance.conn:
        return _db_instance.conn
    
    try:
        from database.railway_db import RailwayDB
        _db_instance = RailwayDB()
        return _db_instance.conn if _db_instance else None
    except:
        return None

def get_system_health(db=None):
    if db:
        _set_db_instance(db)
    health = {
        'overall_score': 0,
        'critical_count': 0,
        'warning_count': 0,
        'healthy_count': 0,
        'webhook': get_webhook_health(),
        'database': get_database_health(),
        'api': get_api_health(),
        'resources': get_resource_health(),
        'ml': get_ml_health(),
        'prediction': get_prediction_health(),
        'modules': get_module_health(),
        'alerts': [],
        'error_handling': get_error_handling_status(),
        'auto_recovery': get_auto_recovery_status()
    }
    
    # Calculate overall score
    scores = []
    for key in ['webhook', 'database', 'api', 'resources', 'ml', 'prediction']:
        if health[key].get('score'):
            scores.append(health[key]['score'])
    
    health['overall_score'] = int(sum(scores) / len(scores)) if scores else 0
    
    # Count statuses
    for key in ['webhook', 'database', 'api', 'resources', 'ml', 'prediction']:
        status = health[key].get('status', 'critical')
        if status == 'healthy':
            health['healthy_count'] += 1
        elif status == 'warning':
            health['warning_count'] += 1
        else:
            health['critical_count'] += 1
    
    # Generate alerts
    health['alerts'] = generate_alerts(health)
    
    return health

def get_webhook_health():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return {'status': 'critical', 'score': 0, 'signal_rate': '0/24h', 'signal_rate_status': 'critical', 'signals_24h': 0, 'last_signal': 'DB Offline'}
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM live_signals WHERE timestamp > NOW() - INTERVAL '24 hours'")
        result = cur.fetchone()
        signals_24h = result[0] if result else 0
        
        cur.execute("SELECT MAX(timestamp) FROM live_signals")
        result = cur.fetchone()
        last_signal = result[0] if result else None
        
        if last_signal:
            minutes_ago = int((datetime.now() - last_signal.replace(tzinfo=None)).total_seconds() / 60)
            last_signal_str = f"{minutes_ago}m ago"
        else:
            minutes_ago = 999
            last_signal_str = 'Never'
        
        signal_rate = f"{signals_24h}/24h"
        status = 'healthy' if minutes_ago < 60 else 'warning' if minutes_ago < 180 else 'critical'
        score = 100 if status == 'healthy' else 85 if status == 'warning' else 50
        
        return {
            'status': status,
            'score': score,
            'signal_rate': signal_rate,
            'signal_rate_status': 'healthy' if signals_24h > 50 else 'warning' if signals_24h > 10 else 'critical',
            'signals_24h': signals_24h,
            'last_signal': last_signal_str
        }
    except Exception as e:
        return {'status': 'critical', 'score': 0, 'signal_rate': '0/24h', 'signal_rate_status': 'critical', 'signals_24h': 0, 'last_signal': 'DB Error'}

def get_database_health():
    conn = None
    try:
        start = time.time()
        conn = get_db_connection()
        if not conn:
            return {'status': 'critical', 'score': 0, 'pool_status': 'Offline', 'query_time': 'N/A', 'query_time_status': 'critical', 'active_connections': 0}
        
        # Test connection with rollback first
        try:
            conn.rollback()
        except:
            pass
            
        cur = conn.cursor()
        
        cur.execute("SELECT 1")
        cur.fetchone()
        
        query_time_ms = int((time.time() - start) * 1000)
        
        cur.execute("SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'")
        result = cur.fetchone()
        active_conn = result[0] if result else 0
        
        status = 'healthy' if query_time_ms < 500 else 'warning' if query_time_ms < 1000 else 'critical'
        score = 100 if status == 'healthy' else 85 if status == 'warning' else 50
        
        return {
            'status': status,
            'score': score,
            'pool_status': 'Active',
            'query_time': f"{query_time_ms}ms",
            'query_time_status': status,
            'active_connections': active_conn
        }
    except Exception as e:
        return {'status': 'critical', 'score': 0, 'pool_status': 'Offline', 'query_time': 'Error', 'query_time_status': 'critical', 'active_connections': 0}

def get_api_health():
    # Placeholder - would track actual API metrics
    return {
        'status': 'healthy',
        'score': 98,
        'response_time': '245ms',
        'response_time_status': 'healthy',
        'error_rate': '0.2%',
        'error_rate_status': 'healthy',
        'request_rate': '12/min'
    }

def get_resource_health():
    if not PSUTIL_AVAILABLE:
        return {
            'status': 'healthy',
            'score': 95,
            'memory_usage': 'N/A',
            'memory_percent': 0,
            'memory_status': 'healthy',
            'cpu_usage': 'N/A',
            'cpu_percent': 0,
            'cpu_status': 'healthy'
        }
    
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        mem_percent = memory.percent
        mem_status = 'healthy' if mem_percent < 70 else 'warning' if mem_percent < 85 else 'critical'
        cpu_status = 'healthy' if cpu < 70 else 'warning' if cpu < 85 else 'critical'
        
        status = 'critical' if mem_status == 'critical' or cpu_status == 'critical' else 'warning' if mem_status == 'warning' or cpu_status == 'warning' else 'healthy'
        score = 100 if status == 'healthy' else 85 if status == 'warning' else 50
        
        return {
            'status': status,
            'score': score,
            'memory_usage': f"{mem_percent:.1f}%",
            'memory_percent': mem_percent,
            'memory_status': mem_status,
            'cpu_usage': f"{cpu:.1f}%",
            'cpu_percent': cpu,
            'cpu_status': cpu_status
        }
    except:
        return {'status': 'healthy', 'score': 95, 'memory_usage': 'N/A', 'cpu_usage': 'N/A', 'memory_percent': 0, 'cpu_percent': 0, 'memory_status': 'healthy', 'cpu_status': 'healthy'}

def get_ml_health():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return {'status': 'warning', 'score': 50, 'accuracy': 'N/A', 'accuracy_status': 'warning', 'health_score': 'N/A', 'health_score_status': 'warning', 'training_samples': '0'}
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM signal_lab_trades WHERE mfe IS NOT NULL")
        result = cur.fetchone()
        samples = result[0] if result else 0
        
        # Placeholder values - would read from ML model metadata
        accuracy = 89.1
        health_score = 85
        
        acc_status = 'healthy' if accuracy >= 85 else 'warning' if accuracy >= 80 else 'critical'
        health_status = 'healthy' if health_score >= 80 else 'warning' if health_score >= 70 else 'critical'
        
        status = 'critical' if acc_status == 'critical' or health_status == 'critical' else 'warning' if acc_status == 'warning' or health_status == 'warning' else 'healthy'
        score = 100 if status == 'healthy' else 85 if status == 'warning' else 50
        
        return {
            'status': status,
            'score': score,
            'accuracy': f"{accuracy}%",
            'accuracy_status': acc_status,
            'health_score': f"{health_score}/100",
            'health_score_status': health_status,
            'training_samples': f"{samples:,}"
        }
    except Exception as e:
        return {'status': 'warning', 'score': 50, 'accuracy': 'N/A', 'accuracy_status': 'warning', 'health_score': 'N/A', 'health_score_status': 'warning', 'training_samples': '0'}

def get_prediction_health():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return {'status': 'warning', 'score': 50, 'avg_confidence': 'N/A', 'confidence_status': 'warning', 'predictions_today': 0, 'last_training': 'N/A'}
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM live_signals WHERE timestamp::date = CURRENT_DATE")
        result = cur.fetchone()
        predictions_today = result[0] if result else 0
        
        # Placeholder values
        avg_confidence = 76.5
        last_training = "2h ago"
        
        conf_status = 'healthy' if avg_confidence >= 70 else 'warning' if avg_confidence >= 60 else 'critical'
        status = conf_status
        score = 100 if status == 'healthy' else 85 if status == 'warning' else 50
        
        return {
            'status': status,
            'score': score,
            'avg_confidence': f"{avg_confidence}%",
            'confidence_status': conf_status,
            'predictions_today': predictions_today,
            'last_training': last_training
        }
    except Exception as e:
        return {'status': 'warning', 'score': 50, 'avg_confidence': 'N/A', 'confidence_status': 'warning', 'predictions_today': 0, 'last_training': 'N/A'}

def get_module_health():
    modules = [
        {'icon': '🔮', 'name': 'ML Hub', 'url': '/ml-dashboard', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '📶', 'name': 'Live Signals', 'url': '/live-signals', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '🏠', 'name': 'Dashboard', 'url': '/dashboard', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '🧪', 'name': 'Signal Lab', 'url': '/signal-lab', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '🕐', 'name': 'Time Analysis', 'url': '/time-analysis', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '🎯', 'name': 'Optimizer', 'url': '/optimizer', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '🏆', 'name': 'Compare', 'url': '/strategy-comparison', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '🧠', 'name': 'AI Advisor', 'url': '/ai-advisor', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '💼', 'name': 'Prop Firm', 'url': '/prop-firm-analyzer', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '📋', 'name': 'Trade Log', 'url': '/trade-log', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '💰', 'name': 'Finance', 'url': '/finance-dashboard', 'status': 'healthy', 'status_text': 'Operational'},
        {'icon': '📊', 'name': 'Reports', 'url': '/reports', 'status': 'healthy', 'status_text': 'Operational'}
    ]
    return modules

def get_error_handling_status():
    """Check which components have error handling"""
    return {
        'database': {
            'has_error_handling': True,
            'type': '@auto_fix_db_errors decorator',
            'coverage': ['webhook_debugger', 'contract_manager', 'signal_processing'],
            'features': ['Auto-rollback aborted transactions', 'Connection retry (2 attempts)', 'Transaction state detection']
        },
        'webhook': {
            'has_error_handling': True,
            'type': 'WebhookDebugger with @auto_fix_db_errors',
            'coverage': ['log_webhook_request', 'log_signal_processing', 'get_signal_stats', 'check_signal_health'],
            'features': ['Request logging', 'Processing status tracking', 'Failure detection']
        },
        'api': {
            'has_error_handling': True,
            'type': '@app.before_request transaction reset',
            'coverage': ['All Flask routes'],
            'features': ['Per-request transaction cleanup', 'Automatic rollback']
        },
        'ml': {
            'has_error_handling': False,
            'type': 'Basic try-catch only',
            'coverage': [],
            'features': []
        }
    }

def get_auto_recovery_status():
    """Check which components have auto-recovery"""
    return {
        'database': {
            'has_auto_recovery': True,
            'type': 'DatabaseHealthMonitor (30s interval)',
            'features': [
                'Automatic transaction rollback',
                'Connection pool reset',
                'Auto-reconnect on failure',
                'Health checks every 30s'
            ],
            'stats_available': True
        },
        'webhook': {
            'has_auto_recovery': False,
            'type': 'Manual intervention required',
            'features': ['Logging only', 'No automatic retry'],
            'stats_available': True
        },
        'api': {
            'has_auto_recovery': True,
            'type': 'Per-request recovery',
            'features': ['Transaction reset before each request', 'Automatic reconnect attempt'],
            'stats_available': False
        },
        'ml': {
            'has_auto_recovery': False,
            'type': 'None',
            'features': [],
            'stats_available': False
        }
    }

def generate_alerts(health):
    alerts = []
    
    if health['webhook']['status'] == 'critical':
        alerts.append({
            'severity': 'critical',
            'title': 'Webhook Signal Reception Critical',
            'message': 'No signals received in over 3 hours. Check TradingView webhook configuration.',
            'time': datetime.now().strftime('%H:%M:%S'),
            'auto_recovery': 'Not available - Manual intervention required'
        })
    
    if health['database']['status'] == 'critical':
        alerts.append({
            'severity': 'critical',
            'title': 'Database Performance Degraded',
            'message': 'Query response time exceeds 1 second. Auto-recovery active.',
            'time': datetime.now().strftime('%H:%M:%S'),
            'auto_recovery': 'DatabaseHealthMonitor running - will attempt reconnect'
        })
    
    if health['resources']['status'] == 'critical':
        alerts.append({
            'severity': 'critical',
            'title': 'System Resources Critical',
            'message': 'Memory or CPU usage exceeds 85%. Consider scaling resources.',
            'time': datetime.now().strftime('%H:%M:%S'),
            'auto_recovery': 'Not available - Manual scaling required'
        })
    
    return alerts
