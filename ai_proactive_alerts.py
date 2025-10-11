"""
AI Proactive Alert System - Monitors trading and sends intelligent alerts
"""
from datetime import datetime, timedelta

def check_performance_alerts(db):
    """Check for performance degradation"""
    cursor = db.cursor(dictionary=True)
    alerts = []
    
    # Win rate drop
    cursor.execute("""
        SELECT 
            AVG(CASE WHEN mfe_none > 0 THEN 1 ELSE 0 END) as current_wr
        FROM signal_lab_trades
        WHERE date > CURRENT_DATE - INTERVAL '7 days'
    """)
    current = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            AVG(CASE WHEN mfe_none > 0 THEN 1 ELSE 0 END) as prev_wr
        FROM signal_lab_trades
        WHERE date BETWEEN CURRENT_DATE - INTERVAL '14 days' AND CURRENT_DATE - INTERVAL '7 days'
    """)
    previous = cursor.fetchone()
    
    if current and previous and current['current_wr'] and previous['prev_wr']:
        drop = (previous['prev_wr'] - current['current_wr']) * 100
        if drop > 15:
            alerts.append({
                'type': 'performance_drop',
                'severity': 'high',
                'message': f"Win rate dropped {drop:.1f}% this week",
                'action': 'Review recent trades and market conditions'
            })
    
    # Consecutive losses
    cursor.execute("""
        SELECT date, mfe_none FROM signal_lab_trades
        WHERE date > CURRENT_DATE - INTERVAL '3 days'
        ORDER BY date DESC, time DESC
        LIMIT 10
    """)
    recent = cursor.fetchall()
    consecutive_losses = 0
    for trade in recent:
        if trade['mfe_none'] < 0:
            consecutive_losses += 1
        else:
            break
    
    if consecutive_losses >= 3:
        alerts.append({
            'type': 'losing_streak',
            'severity': 'critical',
            'message': f"{consecutive_losses} consecutive losses detected",
            'action': 'Stop trading and review strategy'
        })
    
    cursor.close()
    return alerts

def check_opportunity_alerts(db):
    """Check for missed opportunities"""
    cursor = db.cursor(dictionary=True)
    alerts = []
    
    # High-performing session underutilized
    cursor.execute("""
        SELECT session, 
               COUNT(*) as trades,
               AVG(mfe_none) as avg_r
        FROM signal_lab_trades
        WHERE date > CURRENT_DATE - INTERVAL '30 days'
        GROUP BY session
        HAVING AVG(mfe_none) > 2 AND COUNT(*) < 10
    """)
    opportunities = cursor.fetchall()
    
    for opp in opportunities:
        alerts.append({
            'type': 'opportunity',
            'severity': 'medium',
            'message': f"{opp['session']} session averaging {opp['avg_r']:.1f}R but only {opp['trades']} trades",
            'action': f"Increase trading during {opp['session']}"
        })
    
    cursor.close()
    return alerts

def get_all_alerts(db):
    """Get all active alerts"""
    return {
        'performance': check_performance_alerts(db),
        'opportunities': check_opportunity_alerts(db),
        'timestamp': datetime.now().isoformat()
    }
