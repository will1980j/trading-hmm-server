"""
Database Resilience Monitoring and Reporting
Provides real-time metrics on database health and auto-recovery actions
"""
from database.resilient_connection import get_resilient_db
import logging

logger = logging.getLogger(__name__)

def get_resilience_status():
    """Get comprehensive resilience system status"""
    db = get_resilient_db()
    health = db.get_health_status()
    
    metrics = health['metrics']
    success_rate = health['success_rate']
    
    # Determine overall status
    if not health['healthy']:
        status = 'critical'
        status_text = '🔴 Critical'
    elif success_rate < 95:
        status = 'warning'
        status_text = '🟡 Degraded'
    else:
        status = 'healthy'
        status_text = '🟢 Healthy'
    
    return {
        'status': status,
        'status_text': status_text,
        'success_rate': f"{success_rate:.1f}%",
        'metrics': {
            'total_queries': metrics['total_queries'],
            'failed_queries': metrics['failed_queries'],
            'reconnections': metrics['reconnections'],
            'transaction_rollbacks': metrics['transaction_rollbacks'],
            'pool_resets': metrics['pool_resets']
        },
        'features': [
            'Automatic reconnection on all error types',
            'Connection pooling with health monitoring',
            'Transaction state management',
            'Query retry with exponential backoff',
            'Real-time metrics and alerting'
        ],
        'pool_size': health['pool_size']
    }

def get_recovery_recommendations():
    """Get recommendations based on current metrics"""
    db = get_resilient_db()
    health = db.get_health_status()
    metrics = health['metrics']
    
    recommendations = []
    
    if metrics['reconnections'] > 10:
        recommendations.append({
            'severity': 'warning',
            'message': f"High reconnection count ({metrics['reconnections']}). Check network stability.",
            'action': 'Monitor Railway PostgreSQL connection stability'
        })
    
    if metrics['transaction_rollbacks'] > 20:
        recommendations.append({
            'severity': 'warning',
            'message': f"High rollback count ({metrics['transaction_rollbacks']}). Review transaction handling.",
            'action': 'Check for long-running transactions or deadlocks'
        })
    
    if health['success_rate'] < 95:
        recommendations.append({
            'severity': 'critical',
            'message': f"Success rate below 95% ({health['success_rate']:.1f}%). Database issues detected.",
            'action': 'Check Railway PostgreSQL logs and resource usage'
        })
    
    if not recommendations:
        recommendations.append({
            'severity': 'info',
            'message': 'All systems operating normally',
            'action': 'No action required'
        })
    
    return recommendations
